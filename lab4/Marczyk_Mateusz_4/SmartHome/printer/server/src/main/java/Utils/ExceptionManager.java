package Utils;

import Demo.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class ExceptionManager {

    private static final List<Color> supportedColors = Arrays.asList(
            Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW,
            Color.PURPLE, Color.ORANGE, Color.WHITE, Color.PINK,
            Color.CYAN, Color.LIME
    );

    private static final List<Fragrance> supportedFragrances = Arrays.asList(
            Fragrance.LAVENDER, Fragrance.CITRUS, Fragrance.VANILLA,
            Fragrance.ROSE, Fragrance.OCEAN, Fragrance.FRESHLINEN,
            Fragrance.SANDALWOOD, Fragrance.JASMINE, Fragrance.PEPPERMINT,
            Fragrance.EUCALYPTUS
    );
    public static void unsupportedColorException(Color color) throws UnsupportedColorException {
        if(!supportedColors.contains(color)) {
            String reason = "Color " + color + " is not supported";
            throw new UnsupportedColorException(reason);
        }
    }

    public static void unsupportedFragranceException(Fragrance fragrance) throws UnsupportedFragranceException{
        if(!supportedFragrances.contains(fragrance)) {
            String reason = "Fragrance " + fragrance + " is not supported";
            throw new UnsupportedFragranceException(reason);
        }
    }

    public static void valueOutOfRangeException(int minvalue, int maxvalue, int value) throws ValueOutOfRangeException {
        if(value < minvalue || value > maxvalue) {
            String reason = "value value " + value + " is out of range [" + minvalue + ", " + maxvalue + "]";
            throw new ValueOutOfRangeException(reason);
        }
    }
}
