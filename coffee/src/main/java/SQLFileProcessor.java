import java.io.*;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class SQLFileProcessor {
    private static final String SOURCE_PATH = "C:/Users/root/Desktop/SQL脚本处理/原始数据/测试数据/";
    private static final String RESULT_PATH = "C:/Users/root/Desktop/SQL脚本处理/结果数据/结果.sql";
    private static final int BATCH_SIZE = 5000;

    public static void main(String[] args) {
        long startTime = System.currentTimeMillis();

        File[] files = new File(SOURCE_PATH).listFiles((dir, name) -> name.endsWith(".sql"));
        List<String> futures = Arrays.stream(Optional.ofNullable(files).orElse(new File[0]))
                .parallel().map(SQLFileProcessor::processFile).collect(Collectors.toList());
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(RESULT_PATH))) {
            for (String future : futures) {
                writer.write(future);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        long endTime = System.currentTimeMillis();
        System.out.println("处理完成，总耗时：" + (endTime - startTime) + "ms");
    }

    private static String processFile(File file) {
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            StringBuilder result = new StringBuilder();
            String line;
            int count = 0;

            while ((line = reader.readLine()) != null) {
                int valuesIndex = line.indexOf("VALUES");
                int lastParenIndex = line.lastIndexOf(")");
                String valuePart = new StringBuilder(line).substring(valuesIndex + 6, lastParenIndex + 1);
                if (count % BATCH_SIZE == 0) {
                    if (count != 0) {
                        result.append(";\n");
                    }
                    result.append(line, 0, valuesIndex + 6);
                } else {
                    result.append(",");
                }
                result.append(valuePart);
                count++;
            }

            result.append(";\n");
            return result.toString();
        } catch (Exception e) {
            System.out.println("处理文件" + file.getName() + "时出错：" + e.getMessage());
            return null;
        }
    }
}