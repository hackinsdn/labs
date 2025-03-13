# Roteiro de Laboratório - DDoS Ataques de Negação de Serviço Distribuídos

Neste laboratório vamos explorar os ataques de negação de serviço distribuídos, ou simplesmente **DDoS** (do inglês _Distributed Denial of Service_), cujo objetivo geral é indisponibilizar um serviço, usuário ou aplicação através do envio de tráfego malicioso originado em fontes distribuídas ou diversas. Existem diversos tipos de ataques DDoS, destacando-se: DDoS volumétrico; DDoS refletido e amplificado; e _Slow DDoS_. Alguns autores propõem classificações adicionais/diferentes, portanto a lista acima apresenta alguns tipos mais comuns e que serão explorados neste laboratório.

O cenário utilizado para esse laboratório é ilustrado na figura abaixo:

![Topology](https://raw.githubusercontent.com/hackinsdn/labs/refs/heads/feat/lab04-ddos/lab04-ddos/images/topology.png)

Nesse cenário, uma organização fictícia que hospeda o site "HackInSDN.com" será vítima de ataques de negação de serviço distribuídos, tendo como alvo principal o servidor **srv1** que hospeda o site da organização. O atancante orquestra os ataques através do host **c2c** (ou C&C, do inglês _Command and Control_) que gerencia uma botnet de hosts comprometidos (h2, h4, .., h6, h8, h9) utilizados para disparar de fato o ataque. Clientes legítimos como o host **h1** (e também h3 e h7) serão impactados pelo ataque e observarão impacto na disponibilidade do site. Além do processo de orquestração e execução do ataque, este experimento também ilustra técnicas para detecção e contenção de tais ataques.

## Atividade 1 - Testes de funcionamento normal do cenário

TODO

## Atividade 2 - Orquestrando a formação da botnet

TODO

## Atividade 3 - Executando ataques de DDoS volumétrico

TODO

## Atividade 4 - Mitigando ataques de DDoS volumétrico

TODO

## Atividade 5 - Executando ataques de Slow DDoS

TODO

## Atividade 6 - Mitigando ataques de Slow DDoS

TODO
