// author: HackInSDN Team
// version: 1.0
// date: Jan 31, 2025
// description: DDoS Detection and Containment using Kytos SDN Orchestrator
// copyright: Copyright (c) HackInSDN
//
// Based on
//  - https://blog.sflow.com/2018/04/onos-measurement-based-control.html
//  - https://github.com/sflow-rt/ddos-protect/blob/master/scripts/ddos.js
// References:
//  - https://github.com/sflow-rt/ddos-protect/blob/master/scripts/ddos.js
//  - https://sflow-rt.com/reference.php
var user = 'kytosuser';
var password = 'kytospwd';
var kytosserver = '127.0.0.1';
var ifIndexesUrl = "http://127.0.0.1:8050/ifindexes";
var controls = {};
var ifindexes = {};

function fetchIfIndexes(retry) {
  var resp = http2({
    url:ifIndexesUrl,
    headers:{'Accept':'application/json'},
    operation:'get',
  });
  ifindexes = JSON.parse(resp.body);
  if (resp.status == 200) {
    logInfo("HackInSDN DDoS - topology updated (ifIndexes)")
    return;
  }
  if (retry == 0) {
    logWarning("HackInSDN DDoS - Failed to obtain topology (wont be able to process alerts)");
    return;
  }
  setTimeout(fetchIfIndexes, 2000, retry - 1);
  logWarning("HackInSDN DDoS - Temporary failure to obtain topology, trying again... " + retry);
}
fetchIfIndexes(5);

var keys = 'ipdestination';
var filter = 'first:stack:.:ip:ip6=ip';
var value = 'frames';
var values = 'count:ipsource,avg:ipbytes';
var flow_t = '2';
var threshold_t = '10';
var sourceCountFilterThreshold = 10;

var keys6 = 'ip6destination,group:ip6destination:ddos_protect';
var values6 = 'count:ip6source,avg:ip6bytes';
var filter6 = 'first:stack:.:ip:ip6=ip6';

var settings = {
  ip_fragmentation:{threshold:1000},
  icmp_flood:{threshold:1000},
  udp_amplification:{threshold:1000},
  udp_flood:{threshold:1000},
  tcp_amplification:{threshold:1000},
  tcp_flood:{threshold:1000},
  action:"drop",
  redirect_to:null,
};


setFlow('ddos_protect_ip_fragmentation', {
  keys:keys+',ipprotocol',
  value:value,
  values:values,
  filter:'(ipflags=001|range:ipfragoffset:1=true)&'+filter,
  t:flow_t
});
setFlow('ddos_protect_udp_flood', {
  keys:keys+',udpdestinationport',
  value:value,
  values:values,
  filter:'ipprotocol=17&'+filter,
  t:flow_t
});
setFlow('ddos_protect_icmp_flood', {
  keys:keys+',icmptype',
  value:value,
  values:values,
  filter:'ipprotocol=1&'+filter,
  t:flow_t
});
setFlow('ddos_protect_tcp_flood', {
  keys:keys+',tcpdestinationport',
  value:value,
  values:values,
  filter:'ipprotocol=6&'+filter,
  t:flow_t
});
setFlow('ddos_protect_ip6_fragmentation', {
  keys: keys6+',ip6nexthdr',
  value:value,
  values:values6,
  filter:'(ip6fragm=yes|range:ip6fragoffset:1=true)&'+filter6,
  t:flow_t
});
setFlow('ddos_protect_udp6_flood', {
  keys:keys6+',udpdestinationport',
  value:value,
  values:values6,
  filter:'ip6nexthdr=17&'+filter6,
  t:flow_t
});
setFlow('ddos_protect_icmp6_flood', {
  keys:keys6+',icmp6type',
  value:value,
  values:values6,
  filter:'ip6nexthdr=58&'+filter6,
  t:flow_t
});
setFlow('ddos_protect_tcp6_flood', {
  keys:keys6+',tcpdestinationport',
  value:value,
  values:values6,
  filter:'ip6nexthdr=6&'+filter6,
  t:flow_t
});

setThreshold('ddos_protect_icmp_flood',
  {metric:'ddos_protect_icmp_flood', value:settings.icmp_flood.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_icmp6_flood',
  {metric:'ddos_protect_icmp6_flood', value:settings.icmp_flood.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_tcp_flood',
  {metric:'ddos_protect_tcp_flood', value:settings.tcp_flood.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_tcp6_flood',
  {metric:'ddos_protect_tcp6_flood', value:settings.tcp_flood.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_udp_flood',
  {metric:'ddos_protect_udp_flood', value:settings.udp_flood.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_udp6_flood',
  {metric:'ddos_protect_udp6_flood', value:settings.udp_flood.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_ip_fragmentation',
  {metric:'ddos_protect_ip_fragmentation', value:settings.ip_fragmentation.threshold, byFlow:true, timeout:threshold_t}
);
setThreshold('ddos_protect_ip6_fragmentation',
  {metric:'ddos_protect_ip6_fragmentation', value:settings.ip_fragmentation.threshold, byFlow:true, timeout:threshold_t}
);



setEventHandler(function(evt) {
  logInfo("HackInSDN DDoS - received event " + JSON.stringify(evt));
  // TODO: don't consider inter-switch links
  var port = ifindexes[evt.dataSource];
  if(!port) {
    logInfo("HackInSDN DDoS - received event from unknown port. Aborting!");
    return;
  }

  // need OpenFlow info to create filtering rule
  if(!port.dpid || !port.port_no) {
    logWarning("HackInSDN DDoS - Failed to get port information. Ignoring..");
    return;
  }

  var key = evt.thresholdID+'-'+evt.flowKey;
  if(controls[key]) {
    logWarning("HackInSDN DDoS - Already blocked. Ignoring..");
    return;
  }

  var [target,protocol] = evt.flowKey.split(',');
  var [attackers,packetsize] = evt.values ? evt.values : [0,0];

  // avoid false positives by ignoring events with small number of attackers
  if(attackers > 0 && attackers < sourceCountFilterThreshold) {
    logWarning("HackInSDN DDoS - Aborting: source count "+attackers+" too small for "+evt.thresholdID+" "+target+" "+protocol);
    return;
  }

  var kytos_match = {};

  switch(evt.thresholdID) {
    case 'ddos_protect_icmp_flood':
      kytos_match = {
        'vlan': 0,
        'ipv4_dst': target,
        'icmp_type': parseInt(protocol),
      };
      break;
    case 'ddos_protect_icmp6_flood':
      kytos_match = {
        'vlan': 0,
        'ipv6_dst': target,
        'icmp_type': parseInt(protocol),
      };
      break;
    case 'ddos_protect_tcp_flood':
      kytos_match = {
        'vlan': 0,
        'ipv4_dst': target,
        'tcp_dst': parseInt(protocol),
      };
      break;
    case 'ddos_protect_tcp6_flood':
      kytos_match = {
        'vlan': 0,
        'ipv6_dst': target,
        'tcp_dst': parseInt(protocol),
      };
      break;
    case 'ddos_protect_udp_flood':
      kytos_match = {
        'vlan': 0,
        'ipv4_dst': target,
        'udp_dst': parseInt(protocol),
      };
      break;
    case 'ddos_protect_udp6_flood':
      kytos_match = {
        'vlan': 0,
        'ipv6_dst': target,
        'udp_dst': parseInt(protocol),
      };
      break;
    case 'ddos_protect_ip_fragmentation':
      kytos_match = {
        'vlan': 0,
        'ipv4_dst': target,
        'ip_proto': parseInt(protocol),
      };
      break;
    case 'ddos_protect_ip6_fragmentation':
      kytos_match = {
        'vlan': 0,
        'ipv6_dst': target,
        'ip_proto': parseInt(protocol),
      };
      break;
  }
  var match_str = JSON.stringify(kytos_match)
  logInfo("HackInSDN DDoS - detected "+evt.thresholdID+" match="+match_str+" attackers="+attackers+" packetsize="+packetsize);

  var msg = {
    switch: port.dpid,
    interface: port.port_no,
    match:kytos_match,
  };

  if (settings.action == "redirect" && settings.redirect_to) {
    msg.redirect_to = {outport:settings.redirect_to};
  }

  var resp = http2({
    url:'http://'+kytosserver+':8181/api/hackinsdn/containment/v1/',
    headers:{'Content-Type':'application/json','Accept':'application/json'},
    operation:'post',
    user:user,
    password:password,
    body: JSON.stringify(msg)
  });

  if (resp.status != 200) {
    logWarning("HackInSDN DDoS - Failed to submit Kytos containment request: " + resp.body);
    return;
  }

  var resp_json = JSON.parse(resp.body);
  if (!resp_json) {
    logWarning("HackInSDN DDoS - Failed to parse Kytos containment response: " + resp.body);
    return;
  }
  controls[key] = {
    time:Date.now(),
    threshold:evt.thresholdID,
    agent:evt.agent,
    metric:evt.dataSource+'.'+evt.metric,
    flowKey:evt.flowKey,
    containmentId:resp_json.containment_id,
  };

  logInfo("HackInSDN DDoS - Blocked match="+match_str+" containment_id="+resp_json.containment_id);
},[
 'ddos_protect_icmp_flood',
 'ddos_protect_icmp6_flood',
 'ddos_protect_tcp_flood',
 'ddos_protect_tcp6_flood',
 'ddos_protect_udp_flood',
 'ddos_protect_udp6_flood',
 'ddos_protect_ip_fragmentation',
 'ddos_protect_ip6_fragmentation',
]);


setIntervalHandler(function() {
 var now = Date.now();
 for(var key in controls) {
   let rec = controls[key];

   // keep control for at least 10 seconds
   if(now - rec.time < 10000) continue;
   // keep control if threshold still triggered
   if(thresholdTriggered(rec.threshold,rec.agent,rec.metric,rec.flowKey)) continue;

   var resp = http2({
    url:'http://'+kytosserver+':8181/api/hackinsdn/containment/v1/'
        +encodeURIComponent(rec.containmentId),
    headers:{'Accept':'application/json'},
    operation:'delete',
    user:user,
    password:password
   });

   delete controls[key];

   logInfo("HackInSDN DDoS - unblocking " + key + " containment_id="+rec.containmentId);
 }
}, 5);

setHttpHandler(function(request) {
  if (request.method == "GET") {
    return settings;
  }
  if (request.method != "POST") {
    return "Unsupported request";
  }
  if (request.body.action) {
    if (request.body.action == "redirect") {
      if (request.body.redirect_to) {
        settings.redirect_to = request.body.redirect_to;
      }
      settings.action = request.body.action;
    } else if (request.body.action == "drop") {
      settings.action = request.body.action;
    } else {
      return "Unsupported request action. Supported actions: drop, redirect";
    }
  }
  return "OK";
});

logInfo("HackInSDN DDoS - initialized");
