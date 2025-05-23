#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 oled(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

String lines[8];
int lineIndex = 0;

void setup() {
  Serial.begin(115200);
  if (!oled.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED init failed");
    while (true);
  }
  oled.clearDisplay();
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);
  oled.setCursor(0, 0);
  oled.println("Waiting for text...");
  oled.display();
}

void loop() {
  static String inputLine = "";

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      if (inputLine == "DONE") {
        oled.clearDisplay();
        showText();
        inputLine = "";
        lineIndex = 0;
      }else if (inputLine.startsWith("Q:") || inputLine.startsWith("A:")) {
        if (lineIndex < 8) {
          lines[lineIndex++] = inputLine;  // Store without prefix
          
        }
        inputLine = "";
      } else {
        inputLine = "";
      }
    } else {
      inputLine += c;
    }
  }
}

void showText() {
  oled.setTextSize(1);
  oled.setTextColor(SSD1306_WHITE);

  const int lineHeight = 8;
  int y = 0;

  for (int i = 0; i < 8 && y < SCREEN_HEIGHT; i++) {
    oled.setCursor(0, y);
    oled.println(lines[i]);
   
    y += lineHeight;
   
  }
  oled.display();
  delay(2000); 
  oled.clearDisplay(); // Wait for 2 seconds
}
