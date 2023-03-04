void setup(){
Serial.begin(9600);
pinMode(LED_BUILTIN, OUTPUT);
}

void loop(){
    for (int x=1;x<=2;x++){
      digitalWrite(LED_BUILTIN, HIGH);
      delay(200);
      digitalWrite(LED_BUILTIN, LOW);
      delay(200);
    }
    delay(1000);
}