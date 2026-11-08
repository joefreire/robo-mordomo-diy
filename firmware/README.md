# Firmware (V2) — ainda não existe

A V1 do robô é estática, sem eletrônica. O firmware entra na V2, num **único ESP32-S3 com PSRAM**
(decisão do projeto), integrado ao Home Assistant.

Escopo previsto (nada definido em pinos ainda — os componentes não foram comprados):

- duas telas SPI no mesmo barramento (rosto ~4" e painel do peito 3,5"), expressões e painel HA;
- servos: cintura, ombros esquerdo/direito, pescoço pan/tilt (mesmas interfaces mecânicas da V1);
- áudio I²S (alto-falante + microfone), LEDs âmbar;
- base com rodas (2 motores com encoder, driver) e auto-carregamento na doca (contatos + IR).

Estrutura planejada: `firmware/esphome/` (configuração ESPHome) e/ou `firmware/arduino/`.
Envelopes e interfaces mecânicas reservados para tudo isso: `documentation/INTERFACES.md`.
