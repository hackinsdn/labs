// Based on https://blog.sflow.com/2018/04/onos-measurement-based-control.html
var user = 'kytosuser';
var password = 'kytospwd';
var kytosserver = '127.0.0.1';
var controls = {};

setFlow('udp_reflection',
 {keys:'ipdestination,udpsourceport',value:'frames'});
setThreshold('udp_reflection_attack',
 {metric:'udp_reflection',value:100,byFlow:true,timeout:2});

setEventHandler(function(evt) {
 // don't consider inter-switch links
 var link = topologyInterfaceToLink(evt.agent,evt.dataSource);
 if(link) return;

 // get port information
 var port = topologyInterfaceToPort(evt.agent,evt.dataSource);
 if(!port) return;

 // need OpenFlow info to create ONOS filtering rule
 if(!port.dpid || !port.ofport) return;

 // we already have a control for this flow
 if(controls[evt.flowKey]) return;

 var [ipdestination,udpsourceport] = evt.flowKey.split(',');
 var msg = {
    switch: port.dpid,
    interface: port.ofport,
    match: {
      'IN_PORT': port.ofport,
      'ETH_TYPE': ethType:'0x800',
      'IPV4_DST': ip:ipdestination+'/32',
      'IP_PROTO': protocol:'17',
      'UDP_SRC': udpPort:udpsourceport,
    }
 };

 var resp = http2({
  url:'http://'+kytosserver+':8181/api/hackinsdn/containment/v1/',
  headers:{'Content-Type':'application/json','Accept':'application/json'},
  operation:'post',
  user:user,
  password:password,
  body: JSON.stringify(msg)
 });

 var containmentId = JSON.parse(resp.body).containment_id;
 controls[evt.flowKey] = {
  time:Date.now(),
  threshold:evt.thresholdID,
  agent:evt.agent,
  metric:evt.dataSource+'.'+evt.metric,
  containmentId:containmentId,
 };

 logInfo("blocking " + evt.flowKey);
},['udp_reflection_attack']);

setIntervalHandler(function() {
 var now = Date.now();
 for(var key in controls) {
   let rec = controls[key];

   // keep control for at least 10 seconds
   if(now - rec.time < 10000) continue;
   // keep control if threshold still triggered
   if(thresholdTriggered(rec.threshold,rec.agent,rec.metric,key)) continue;

   var resp = http2({
    url:'http://'+kytosserver+':8181/api/hackinsdn/containment/v1/'
        +encodeURIComponent(rec.containmentId),
    headers:{'Accept':'application/json'},
    operation:'delete',
    user:user,
    password:password
   });

   delete controls[key];

   logInfo("unblocking " + key);
 }
});
