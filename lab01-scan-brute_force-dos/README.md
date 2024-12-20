# Roteiro de Laboratório - Execução, detecção e contenção de ataques de varredura de portas, brute-force e negação de serviço

Neste laboratório vamos simular um cenário típico de ataques de varredura de portas (scan), ataques para quebra do mecanismo de autenticação (brute-force) e ataques de negação de serviço simples (DoS). Os ataques ocorrerão em um topologia conforme ilustrado na Figura 1.

![Topology](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/topology.png)
*Figura 1: Topologia de Rede do Laboratório*

## Atividade 1 - Acesso aos nós e teste de conectividade

Após a criação do laboratório, você terá a disposição dois servidores virtuais no Kubernetes (chamados de Pods): Kytos e Mininet-Sec. O Mininet-Sec é um emulador de redes responsável pela criação da topologia apresentada na Figura 1. Naquela topologia, parte dos nós são *namespaces de rede do Linux*, outros são switches virtuais do tipo OpenVSwitch e Linux Bridge, e dois deles são também Pods no Kubernetes. Já o Kytos é o orquestrador de redes, responsável pelo gerenciamento de alguns nós da topologia. Nesta atividade, vamos testar o acesso aos nós citados acima e testar a conectividade entre eles.

Clique no link do Serviço "http-mininet-sec" conforme ilustrado abaixo para abrir a interface web do Mininet-Sec:

![Abrir Mininet-Sec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-mininet-sec.png)

Após clicar no serviço Mininet-Sec, uma nova aba do seu navegador web deve ser aberta com a interface web do Mininet-Sec. Caso o Mininet-sec ainda esteja criando a topologia, você verá uma mensagem informando para aguardar alguns segundos até que a topologia seja criada. Após finalizar a criação da topologia, você verá uma imagem como ilustrado abaixo:

![Tela inicial Mininet-sec](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/tela-mininet-sec.png)

Na tela do Mininet-sec, localize o host **h301** (host 3 do AS 300), clique neste host (ele deve mudar de cor para azul) e com o botão direito do mouse escolha a opção "Terminal". O terminal do host h301 deve ser aberto em uma nova aba do seu navegador web. Abaixo ilustramos esse processo:

![Abrir terminal do host h301](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/mnsec-terminal-h301.gif)

Após visualizar o terminal do h301, teste a conectividade com o host srv501 (servidor 1 do AS 500):
```
ping -c 4 172.16.50.1
traceroute -n 172.16.50.1
```

A seguinte saída é esperada para os comandos acima:
```
root@h301:~# ping -c 4 172.16.50.1
PING 172.16.50.1 (172.16.50.1) 56(84) bytes of data.
64 bytes from 172.16.50.1: icmp_seq=1 ttl=61 time=0.395 ms
64 bytes from 172.16.50.1: icmp_seq=2 ttl=61 time=0.152 ms
64 bytes from 172.16.50.1: icmp_seq=3 ttl=61 time=0.169 ms
64 bytes from 172.16.50.1: icmp_seq=4 ttl=61 time=0.166 ms

--- 172.16.50.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3051ms
rtt min/avg/max/mdev = 0.152/0.220/0.395/0.100 ms
root@h301:~# traceroute -n 172.16.50.1
traceroute to 172.16.50.1 (172.16.50.1), 30 hops max, 60 byte packets
 1  192.168.30.254  0.112 ms  0.029 ms  0.026 ms
 2  10.30.0.1  0.064 ms  0.034 ms  0.033 ms
 3  10.30.50.2  0.069 ms  0.049 ms  0.045 ms
 4  172.16.50.1  0.095 ms  0.061 ms  0.059 ms
```

Agora vamos realizar um novo teste de conectividade, desta vez a partir do host **secflood**. O host secflood possui conexões no AS 200 e no AS 400, porém o roteamento deste nós foi configurado para que a saída de Internet ocorra através do AS 200. Execute os passos anteriores para abrir o Terminal mas desta vez do "secflood". Ao acesso o terminal do secflood execute o teste de ping para o srv501:
```
ping -c 4 172.16.50.1
```

Observe que desta vez a saída indica que o host está inalcançável:
```
root@mnsec-secflood1-14bbabbf330b44:/# ping -c 4 172.16.50.1
PING 172.16.50.1 (172.16.50.1) 56(84) bytes of data.
From 192.168.20.10 icmp_seq=1 Destination Host Unreachable
From 192.168.20.10 icmp_seq=2 Destination Host Unreachable

--- 172.16.50.1 ping statistics ---
4 packets transmitted, 0 received, +2 errors, 100% packet loss, time 3067ms
pipe 4
```

Repita o teste acima, porém agora utilizando como destino o IP do firewall **fw201** que é o gateway do secflood:
```
ping -c4 192.168.20.254
```

Novamente a saída indica que o firewall está inalcanável:
```
root@mnsec-secflood1-14bbabbf330b44:/# ping -c4 192.168.20.254
PING 192.168.20.254 (192.168.20.254) 56(84) bytes of data.
From 192.168.20.10 icmp_seq=1 Destination Host Unreachable
From 192.168.20.10 icmp_seq=2 Destination Host Unreachable
From 192.168.20.10 icmp_seq=3 Destination Host Unreachable
From 192.168.20.10 icmp_seq=4 Destination Host Unreachable

--- 192.168.20.254 ping statistics ---
4 packets transmitted, 0 received, +4 errors, 100% packet loss, time 3059ms
pipe 4
```

O comportamento acima é esperado e se dá pelo fato de que o AS200 ainda não foi configurado para prover conectividade entre os nós. O AS 200 possui switches programáveis e uma rede SDN (Rede Definida por Software), cujo controlador é o Kytos (leia mais sobre o Kytos em https://github.com/kytos-ng/). Vamos, portanto, configurar o Kytos para estabelecer a conectividade no AS 200.

Para isso, vamos abrir o console do Kytos através do seguinte link na interface do Dashboard HackInSDN:

![Abrir Kytos](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-kytos.png)

Ao acessar o terminal do Kytos, vamos utilizar a API REST do Kytos para criar uma VPN L2 que interconecta o secflood ao firewall fw201. Para isso, na aba com o terminal do Kytos, execute o seguinte comando:
```
curl -s -H 'Content-type: application/json' -X POST http://127.0.0.1:8181/api/kytos/mef_eline/v2/evc/ -d '{"name": "l2vpn-secflood-to-fw", "dynamic_backup_path": true, "uni_z": {"interface_id": "00:00:00:00:00:00:00:cb:1", "tag": {"tag_type": "vlan", "value": "untagged"}}, "uni_a": {"interface_id": "00:00:00:00:00:00:00:c9:2", "tag": {"tag_type": "vlan", "value": "untagged"}}}' | jq
```

A saída esperada do comando acima é:
```
root@kytos-14bbabbf330b44-75854d5cf8-94j6b:/# curl -s -H 'Content-type: application/json' -X POST http://127.0.0.1:8181/api/kytos/mef_eline/v2/evc/ -d '{"name": "l2vpn-secflood-to-fw", "dynamic_backup_path": true, "uni_z": {"interface_id": "00:00:00:00:00:00:00:cb:1", "tag": {"tag_type": "vlan", "value": "untagged"}}, "uni_a": {"interface_id": "00:00:00:00:00:00:00:c9:2", "tag": {"tag_type": "vlan", "value": "untagged"}}}' | jq
{
  "circuit_id": "348a7bc54f1745",
  "deployed": true
}
root@kytos-14bbabbf330b44-75854d5cf8-94j6b:/# 
```

Agora vamos voltar ao terminal do secflood e realizar novamente os testes de ping:
```
ping -c 4 172.16.50.1
ping -c 4 192.168.20.254
```

O comportamento espero agora indica o sucesso na conectividade do secflood, conforme ilustrado abaixo nos testes entre o secflood e o fw201 e entre o secflood e srv501:
```
root@mnsec-secflood1-14bbabbf330b44:/# ping -c 4 192.168.20.254
PING 192.168.20.254 (192.168.20.254) 56(84) bytes of data.
64 bytes from 192.168.20.254: icmp_seq=1 ttl=64 time=3.35 ms
64 bytes from 192.168.20.254: icmp_seq=2 ttl=64 time=3.35 ms
64 bytes from 192.168.20.254: icmp_seq=3 ttl=64 time=3.38 ms
64 bytes from 192.168.20.254: icmp_seq=4 ttl=64 time=3.35 ms

--- 192.168.20.254 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 3.345/3.357/3.382/0.014 ms

root@mnsec-secflood1-14bbabbf330b44:/# ping -c 4 172.16.50.1
PING 172.16.50.1 (172.16.50.1) 56(84) bytes of data.
64 bytes from 172.16.50.1: icmp_seq=1 ttl=58 time=3.55 ms
64 bytes from 172.16.50.1: icmp_seq=2 ttl=58 time=3.54 ms
64 bytes from 172.16.50.1: icmp_seq=3 ttl=58 time=3.46 ms
64 bytes from 172.16.50.1: icmp_seq=4 ttl=58 time=3.44 ms

--- 172.16.50.1 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3005ms
rtt min/avg/max/mdev = 3.444/3.497/3.546/0.044 ms
```

## Atividade 2 - Ataques de varredura de porta

Os ataques de varredura de porta, também conhecidos como *port scanning*, visam levantar informações sobre um ambiente alvo, incluindo os computadores que estão online, serviços de rede em execução no computador (i.e, portas abertas) e informações sobre o software que recebendo pacotes em determinada porta. A varredura de portas faz parte da fase de reconhecimento de rede e levantamento de informações em um ataque ou exercício de auditoria. Nesta atividade vamos explorar alguns cenários de varredura de porta utilizando a ferramenta **nmap**.

### 2.1 Executando nmap através da interface web do secflood

Na interface web do Dashbaord, clique no link do Serviço "https-secflood" conforme ilustrado abaixo para abrir a interface web do Secflood:

![Abrir Secflood](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/abrir-secflood.png)

Ao clicar no link do serviço, você deve receber um alerta sobre o certificado SSL auto-assinado. Neste ambiente restrito de teste, é seguro ignorar o alerta e processeguir:

![Erro SSL](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/erro-ssl.png)


Você será direcionado ao portal web do secflood, que provê uma interface de usuário para facilitar a utilização das ferramentas de segurança. A tela inicial do Secflood irá solicitar usuário e senha, conforme mostrado abaixo (você pode fornecer os valores hostname = `127.0.0.1`, usuário = `root` e senha = `hackinsdn`)

![Login Secflood](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/login-secflood.png)

Após logar no Secflood, navegue pelo menu à esquerda e clique em "Tools List" e então escolha a ferramenta "nmap".

Na tela de utilização do NMAP existem várias opções que podem ser exploradas. A figura abaixo ilustra algumas destas opções. Você pode clicar no botão "Commands" (número 1 na figura) pra visualizar as opções disponíveis e sintaxe da ferramenta. No botão "+ Options" (número 2 na figura) você pode de fato habilitar parâmetros que customizam o funcionamento do nmap. Por fim, o alvo da varredura de portas pode ser especificado no campo de entrada principal (número 3 na figura). Preencha o alvo do ataque como 172.16.10.1 (número 3 na figura, sinalizado com a seta):

![Secflood NMAP](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-nmap.png)

Após executar o teste de NMAP acima, você deverá obter o seguinte resultado:

![Secflood NMAP Resultado](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/main/lab01-scan-brute_force-dos/images/secflood-nmap-result.png)

Este resultado acima mostra que o SCAN obteve resultados interessantes para o reconhecimento do ambiente, listando duas portas TCP abertas: 80 e 443. O Secflood pode ajudar no processo de eventuais correções para portas indevidamente abertas, bem como é possível salvar o relatório para futura análise.

TODO: falar sobre o scan na linha de comando, abrir o tcpdump no alvo e mostrar os acessos

TODO: falar sobre scan UDP (resolver https://github.com/hackinsdn/secflood/issues/9)
 -  aproveitar pra falar de levantamento de serviços aqui

TODO: falar sobre scan horizontal

TODO: falar sobre scan com NSE

## Atividade 3 - Ataques de brute-force

TODO

## Atividade 4 - Ataques de negação de serviço

TODO

## Atividade 5 - Detecção e contenção de ataques de varredura

TODO
