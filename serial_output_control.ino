void setup()
{
  for (int pin = 2; pin < 54; pin++)
  {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    if (pin == 2)
    {
      pulse_pin(pin);
    }
  }
  Serial.begin(115200);
}

void loop()
{
  receive_data();
  handle_new_data();
}

const byte numChars = 32;
char receivedChars[numChars];

String receivedString;

boolean newData = false;

void receive_data()
{
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false)
  {
    rc = Serial.read();

    if (recvInProgress == true)
    {
      if (rc != endMarker)
      {
        receivedString += rc;
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars)
        {
          ndx = numChars - 1;
        }
      }
      else
      {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }
    else if (rc == startMarker)
    {
      recvInProgress = true;
    }
  }
}

void handle_new_data()
{
  if (newData == true)
  {
    int pin = receivedString.toInt();
    pulse_pin(pin);
    receivedString = "";
    newData = false;
  }
}

void pulse_pin(int pin)
{
  digitalWrite(pin, HIGH);
  delay(100);
  digitalWrite(pin, LOW);
}