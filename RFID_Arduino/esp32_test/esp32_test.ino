


void setup(){
Serial.begin(115200);
}

void loop(){
    Serial.println("hello");
    String text = "world";
    Serial.println(text);
    delay(1000);
}
