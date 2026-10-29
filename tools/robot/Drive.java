import java.awt.Robot;
import java.awt.event.InputEvent;
import java.awt.event.KeyEvent;

// Drive the Xvfb test client: java Drive.java "look 300 0" "key F1" "wait 2000" "click 960 540" "hold W 1500"
// look dx dy  : move the mouse relatively in small steps (turns the camera when the game has the cursor)
public class Drive {
    static int key(String k) throws Exception {
        if (k.length() == 1) return KeyEvent.getExtendedKeyCodeForChar(Character.toLowerCase(k.charAt(0)));
        return KeyEvent.class.getField("VK_" + k.toUpperCase()).getInt(null);
    }
    public static void main(String[] args) throws Exception {
        Robot r = new Robot();
        r.setAutoDelay(15);
        int cx = 960, cy = 540;
        for (String a : args) {
            String[] p = a.split(" ");
            switch (p[0]) {
                case "look": {
                    // GLFW keeps a captured cursor at the window centre, so repeat a small offset from the centre.
                    int dx = Integer.parseInt(p[1]), dy = Integer.parseInt(p[2]);
                    int steps = Math.max(1, Math.max(Math.abs(dx), Math.abs(dy)) / 10);
                    for (int i = 0; i < steps; i++) {
                        r.mouseMove(cx + dx / steps, cy + dy / steps);
                        r.delay(40);
                    }
                    break;
                }
                case "key": { int k = key(p[1]); r.keyPress(k); r.delay(80); r.keyRelease(k); break; }
                case "hold": { int k = key(p[1]); r.keyPress(k); r.delay(Integer.parseInt(p[2])); r.keyRelease(k); break; }
                case "click": {
                    r.mouseMove(Integer.parseInt(p[1]), Integer.parseInt(p[2])); r.delay(150);
                    r.mousePress(InputEvent.BUTTON1_DOWN_MASK); r.delay(100); r.mouseRelease(InputEvent.BUTTON1_DOWN_MASK);
                    break;
                }
                case "move": r.mouseMove(Integer.parseInt(p[1]), Integer.parseInt(p[2])); break;
                case "wait": r.delay(Integer.parseInt(p[1])); break;
                case "type": {   // US layout; shifted symbols handled below
                    String text = a.substring(5);
                    String shifted = "~!@#$%^&*()_+{}|:\"<>?";
                    String base = "`1234567890-=[]\\;',./";
                    for (char c : text.toCharArray()) {
                        boolean shift = Character.isUpperCase(c) || shifted.indexOf(c) >= 0;
                        char k = shifted.indexOf(c) >= 0 ? base.charAt(shifted.indexOf(c)) : Character.toLowerCase(c);
                        int code = KeyEvent.getExtendedKeyCodeForChar(k);
                        if (shift) r.keyPress(KeyEvent.VK_SHIFT);
                        r.keyPress(code); r.keyRelease(code);
                        if (shift) r.keyRelease(KeyEvent.VK_SHIFT);
                    }
                    break;
                }
                default: throw new IllegalArgumentException(a);
            }
        }
    }
}
