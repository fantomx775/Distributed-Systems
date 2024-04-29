module Demo
{
    interface Printer
    {
        void printString(string s);
    }

    interface Bulbulator
    {
        string bulbulate(int b);
    }

    enum Color
    {
        RED,
        GREEN,
        BLUE,
        YELLOW,
        PURPLE,
        ORANGE,
        WHITE,
        PINK,
        CYAN,
        LIME,
    }

    sequence<Color> Colors;

    interface Light
    {
        void turnOn();
        void turnOff();
        bool getState();
    }

    class NormalLight implements Light
    {
        bool state;
    }

    interface LightController
    {
        void setBrightness(int b);
        int getBrightness();
        void setColor(Color c);
        Color getColor();
    }

    class Dimmer implements Light, LightController
    {
        bool state;
        int brightness;
        Colors colors;
        Color color;

    }
}