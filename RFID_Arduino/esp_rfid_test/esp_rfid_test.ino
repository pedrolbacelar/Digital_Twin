/*
 * --------------------------------------------------------------------------------------------------------------------
 * Example sketch/program showing how to read new NUID from a PICC to serial.
 * --------------------------------------------------------------------------------------------------------------------
 * This is a MFRC522 library example; for further details and other examples see: https://github.com/miguelbalboa/rfid
 *
 * Example sketch/program showing how to the read data from a PICC (that is: a RFID Tag or Card) using a MFRC522 based RFID
 * Reader on the Arduino SPI interface.
 *
 * When the Arduino and the MFRC522 module are connected (see the pin layout below), load this sketch into Arduino IDE
 * then verify/compile and upload it. To see the output: use Tools, Serial Monitor of the IDE (hit Ctrl+Shft+M). When
 * you present a PICC (that is: a RFID Tag or Card) at reading distance of the MFRC522 Reader/PCD, the serial output
 * will show the type, and the NUID if a new card has been detected. Note: you may see "Timeout in communication" messages
 * when removing the PICC from reading distance too early.
 *
 * @license Released into the public domain.
 *
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
 * More pin layouts for other boards can be found here: https://github.com/miguelbalboa/rfid#pin-layout
 */

#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <PubSubClient.h>

// lego factory credentials
const char *ssid = "THE FACTORY - ROUTER 2";
const char *password = "legofactory";
const char *mqtt_server = "192.168.0.50";

// my pc credentials
// const char* ssid = "Galaxy A22DB0F";
// const char* password = "tpqv9051";
// const char* mqtt_server = "192.168.2.70";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

#define SS_PIN 5
#define RST_PIN 22

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

MFRC522::MIFARE_Key key;

// Init array that will store new NUID
byte nuidPICC[4];

// counter variable
int count = 1;

void setup()
{
  Serial.begin(115200);
  SPI.begin();     // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522

  for (byte i = 0; i < 6; i++)
  {
    key.keyByte[i] = 0xFF;
  }

  // initiating wifi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
  }
  client.setServer(mqtt_server, 1883);
  Serial.println(F("This code scan the MIFARE Classsic NUID."));
}

void loop()
{
  if (!client.connected())
  {
    Serial.println("not connected");
    reconnect();
  }
  client.loop();

  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been readed
  if (!rfid.PICC_ReadCardSerial())
    return;

  if (rfid.uid.uidByte[0] != nuidPICC[0] ||
      rfid.uid.uidByte[1] != nuidPICC[1] ||
      rfid.uid.uidByte[2] != nuidPICC[2] ||
      rfid.uid.uidByte[3] != nuidPICC[3])
  {
    Serial.println();
    Serial.println(F("New card"));

    // Store NUID into nuidPICC array
    for (byte i = 0; i < 4; i++)
    {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }

    String RFID_ID = printDec(rfid.uid.uidByte, rfid.uid.size);
    Serial.println(RFID_ID);
    // int part_id = count;
    // Serial.println(part_id);
    // String current_id;
    // current_id = String(part_id);

    //--- Copy the String RFID
    String RFID_ID_dict = "{'machine_id':'1','part_id':"+"'"+RFID_ID+"'"+"}";
    //--- Define the array of chars
    char payload[RFID_ID_dict.length() + 1];

    //--- Convert a string into a array of chars
    RFID_ID_dict.toCharArray(payload, sizeof(payload));
    client.publish("part_id",RFID_ID_dict)

    // switch (RFID_ID)
    // {
    // case "22019510149":
    //   client.publish("part_id", "{'machine_id':'1','part_id':'22019510149'}");
    //   break;
    // case "1889810149":
    //   client.publish("part_id", "{'machine_id':'1','part_id':'1889810149'}");
    //   break;
    // case "2049810149":
    //   client.publish("part_id", "{'machine_id':'1','part_id':'2049810149'}");
    //   break;
    // case "2209210149":
    //   client.publish("part_id", "{'machine_id':'1','part_id':'2209210149'}");
    //   break;
    // case "20419710149":
    //   client.publish("part_id", "{'machine_id':'1','part_id':'20419710149'}");
    //   break;
    // default:
    //   client.publish("part_id", "{'machine_id':'1','part_id':'111'}");
    //   break;
    // }

    // Old Implementation
    //    for (int c = 0; c < 4; c++)
    //    {
    //    if (RFID_ID == "22019510149")
    //    {
    //      client.publish("part_id", "{'machine_id':'3','part_id':'1'}");
    //      }
    //    else if (RFID_ID == "1889810149")
    //    {
    //      client.publish("part_id", "{'machine_id':'3','part_id':'2'}");
    //    }
    //    else if (RFID_ID == "2049810149")
    //    {
    //      client.publish("part_id", "{'machine_id':'3','part_id':'3'}");
    //      }
    //    else if (RFID_ID == "2209210149")
    //    {
    //      client.publish("part_id", "{'machine_id':'3','part_id':'4'}");
    //      }
    //    else if (RFID_ID == "20419710149")
    //    {
    //      client.publish("part_id", "{'machine_id':'3','part_id':'5'}");
    //      }
    //    else
    //    {
    //      client.publish("part_id", "{'machine_id':'3','part_id':'111'}");
    //      }

    //   delay(500);
    //   }
    //   //count += 1;
    // }

    else Serial.println(F("Card repeated."));

    // Halt PICC
    rfid.PICC_HaltA();

    // Stop encryption on PCD
    rfid.PCD_StopCrypto1();
  }

  void reconnect()
  {
    while (!client.connected())
    {
      Serial.print("inside reconnect");
      if (client.connect("esp32_client"))
      {
        Serial.println("if client collect");
        // publish Hello
        send_message();
      }
      else
      {
        delay(5000);
      }
    }
  }

  void send_message()
  {
    // publish a message to an MQTT topic
    client.publish("test_topic", "Hello from ESP32!");
    Serial.println("mqtt verification test");
  }

  String printDec(byte * buffer, byte bufferSize)
  {
    String result = "";
    for (byte i = 0; i < bufferSize; i++)
    {
      result += (String)buffer[i];
    }
    return result;
    // for (byte i = 0; i < bufferSize; i++) {
    //   Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    //   Serial.print(buffer[i], DEC);
    //   Serial.print((int)buffer[i]);
    // }
  }

}
