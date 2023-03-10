/*
 * ---------------------------------------------------------------------------------------------------------------------------
 * RFID READER: The ESP32 has a RFID reader (RC522) to read RFID stickers UID (unique ID) and sends the UID through MQTT
 * ---------------------------------------------------------------------------------------------------------------------------
 * Typical pin layout used:
 * -----------------------------------------------------------------------------------------
 *             MFRC522      Arduino       Arduino   Arduino    Arduino          Arduino
 *             Reader/PCD   Uno/101       Mega      Nano v3    Leonardo/Micro   Pro Micro
 * Signal      Pin          Pin           Pin       Pin        Pin              Pin
 * -----------------------------------------------------------------------------------------
 * RST/Reset   RST          9             5         D9         RESET/ICSP-5     RST
 * SPI SS      SDA(SS)      10            53        D10        10               10
 * SPI MOSI    MOSI         11 / ICSP-4   51        D11        ICSP-4           16
 * SPI MISO    MISO         12 / ICSP-1   50        D12        ICSP-1           14
 * SPI SCK     SCK          13 / ICSP-3   52        D13        ICSP-3           15
 *
 */

// ####################### WIFI & IP ADDRESS CONFIGURATION #######################
// lego factory credentials
const char *ssid = "THE FACTORY - ROUTER 2";
const char *password = "legofactory";
const char *mqtt_server = "192.168.0.50";

// my pc credentials
//const char* ssid = "Galaxy A22DB0F";
//const char* password = "tpqv9051";
//const char* mqtt_server = "192.168.15.41";
// ##################################################################################


// ################################### MACHINE ID ###################################
String machine_id = "1";
// ##################################################################################

// ====================================================================================================================================================

// ------------- Libraries -------------
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <PubSubClient.h>
// -------------------------------------

// -------------- Variables Config --------------
WiFiClient wifiClient;
PubSubClient client(wifiClient);
#define SS_PIN 5
#define RST_PIN 22
MFRC522 rfid(SS_PIN, RST_PIN);  // Instance of the class
MFRC522::MIFARE_Key key;
byte nuidPICC[4];
// -----------------------------------------

// -------------------------------------- xxxxxxxxx -------------------------------------------------

void setup() {
  Serial.begin(115200);
  Serial.println("Hello from ESP32");
  SPI.begin();      // Init SPI bus
  rfid.PCD_Init();  // Init MFRC522

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  // initiating wifi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  client.setServer(mqtt_server, 1883);
  Serial.println(F("This code scan the MIFARE Classsic NUID."));
}

// -------------------------------------- xxxxxxxxx -------------------------------------------------

void loop() 
{
  if (!client.connected()) {
    Serial.println("not connected");
    reconnect();
  }
  client.loop();

  // -------------------------------------------- RESET THE LOOP --------------------------------------------
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;
  // ---------------------------------------------------------------------------------------------------------

  // -------------------------------------------- RESET THE LOOP --------------------------------------------
  // Verify if the NUID has been readed
  if (!rfid.PICC_ReadCardSerial())
    return;
  // ---------------------------------------------------------------------------------------------------------

  // ----------------------------------------------- MAIN FUNCTION --------------------------------------------
  if (rfid.uid.uidByte[0] != nuidPICC[0] || rfid.uid.uidByte[1] != nuidPICC[1] || rfid.uid.uidByte[2] != nuidPICC[2] || rfid.uid.uidByte[3] != nuidPICC[3]) {
    Serial.println();
    Serial.println(F("New card"));

    // Store NUID into nuidPICC array
    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }

    // ----------------------- PAYLOAD CONSTRUCTION -----------------------
    String RFID_ID = printDec(rfid.uid.uidByte, rfid.uid.size);
    Serial.println(RFID_ID);
    String RFID_ID_dict = "{'machine_id':'";
    RFID_ID_dict.concat(machine_id);
    RFID_ID_dict.concat("','part_id': '");
    RFID_ID_dict.concat(RFID_ID);
    RFID_ID_dict.concat("'}");
    char payload[RFID_ID_dict.length() + 1];
    RFID_ID_dict.toCharArray(payload, sizeof(payload));
    // --------------------------------------------------------------------

    // --------------------------- PUBLISHING -----------------------------
    for (int c = 0; c < 3; c++)
    {
      client.publish("part_id", payload);
      delay(500);
    }
    // ---------------------------------------------------------------------

  } else Serial.println(F("Card repeated."));

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}
// ---------------------------------------------------------------------------------------------------------


// ---------------------------------------------- EXTERNAL FUNCTIONS ----------------------------------------------
void reconnect() {
  while (!client.connected()) {
    Serial.print("inside reconnect");
    if (client.connect("esp32_client")) {
      Serial.println("if client collect");
      // publish Hello
      send_message();
    } else {
      delay(5000);
    }
  }
}

void send_message() {
  // publish a message to an MQTT topic
  client.publish("test_topic", "Hello from ESP32!");
  Serial.println("mqtt verification test");
}

String printDec(byte *buffer, byte bufferSize) {
  String result = "";
  for (byte i = 0; i < bufferSize; i++) {
    result += (String)buffer[i];
  }
  return result;
}
// ---------------------------------------------------------------------------------------------------------

