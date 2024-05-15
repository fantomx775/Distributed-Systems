module Demo
{

    exception ValueOutOfRangeException
    { string reason; };

    exception UnsupportedColorException
    { string reason; };

    exception UnsupportedFragranceException
    { string reason; };

    interface Printer
    {
        void printString(string s);
    }

    interface Device
    {
        void turnOn();
        void turnOff();
        bool getState();
    }

    interface Bulbulator extends Device
    {
        string bulbulate(int b);
    }

    enum Fragrance
    {
        LAVENDER,
        CITRUS,
        VANILLA,
        ROSE,
        OCEAN,
        FRESHLINEN,
        SANDALWOOD,
        JASMINE,
        PEPPERMINT,
        EUCALYPTUS,
    }

    sequence<Fragrance> Fragrances;

    struct ScheduleBlock
    {
        string startTime;
        string endTime;
        int temperature;
        int humidity;
        Fragrances fragrances;
    }

    sequence<ScheduleBlock> Schedules;

    interface HVAC extends Device
    {
            void setTemperature(int t) throws ValueOutOfRangeException;
            int getTemperature();
            void setHumidity(int h) throws ValueOutOfRangeException;
            int getHumidity();
            void setFragrances(Fragrances f) throws UnsupportedFragranceException;
            Fragrances getFragrances();
            void addSchedule(ScheduleBlock s) throws ValueOutOfRangeException, UnsupportedFragranceException;
            Schedules getSchedules();
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

    interface Light extends Device
    {
    }

    interface LightController extends Device
    {
        void setBrightness(int b) throws ValueOutOfRangeException;
        int getBrightness();
        void setColor(Color c) throws UnsupportedColorException;
        Color getColor();
    }
}