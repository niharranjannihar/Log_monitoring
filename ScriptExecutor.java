import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class ScriptExecutor {

    public static void main(String[] args) {
        // Create a ScheduledExecutorService with a single thread
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

        // Define the interval in minutes (1 or 2)
        int intervalInMinutes = 1;

        // Schedule the task to execute the script at the specified interval
        scheduler.scheduleAtFixedRate(new ScriptRunner(), 0, intervalInMinutes, TimeUnit.MINUTES);
    }
}

class ScriptRunner implements Runnable {
    @Override
    public void run() {
        try {
            // Execute the shell script
            Process process = Runtime.getRuntime().exec("/home/apmosys/Downloads/log_monitoring/test.sh");

            // Wait for the process to finish
            int exitCode = process.waitFor();

            // Check if the process exited successfully
            if (exitCode == 0) {
                System.out.println("Script executed successfully.");
            } else {
                System.err.println("Error: Script execution failed with exit code " + exitCode);
            }
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
