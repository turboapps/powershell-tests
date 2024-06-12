import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

public class HelloWorld extends JFrame {
    public HelloWorld() {
        // Setting up the JFrame
        setTitle("Hello World Application");
        setSize(300, 200);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(EXIT_ON_CLOSE);

        // Panel to hold components
        JPanel panel = new JPanel();

        // Button that shows the message
        JButton button = new JButton("Click Me!");
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                JOptionPane.showMessageDialog(null, "Hello World!");
            }
        });

        // Adding button to the panel
        panel.add(button);

        // Adding panel to the frame
        this.add(panel);
    }

    public static void main(String[] args) {
        // Running the application
        java.awt.EventQueue.invokeLater(new Runnable() {
            public void run() {
                new HelloWorld().setVisible(true);
            }
        });
    }
}
