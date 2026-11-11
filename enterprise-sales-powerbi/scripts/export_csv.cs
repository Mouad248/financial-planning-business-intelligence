using System;
using System.Data;
using System.Globalization;
using System.IO;
using System.Text;

public static class NativeModelCsv
{
    private static string Quote(string text)
    {
        return "\"" + text.Replace("\"", "\"\"") + "\"";
    }

    public static long Export(IDataReader reader, string path, string[] names)
    {
        long count = 0;
        using (var output = new StreamWriter(path, false, new UTF8Encoding(false)))
        {
            var fields = new string[names.Length];
            for (int i = 0; i < names.Length; i++) fields[i] = Quote(names[i]);
            output.WriteLine(string.Join(",", fields));
            while (reader.Read())
            {
                for (int i = 0; i < fields.Length; i++)
                {
                    if (reader.IsDBNull(i)) { fields[i] = ""; continue; }
                    object value = reader.GetValue(i);
                    string text;
                    if (value is DateTime) text = ((DateTime)value).ToString("yyyy-MM-ddTHH:mm:ss", CultureInfo.InvariantCulture);
                    else if (value is bool) text = ((bool)value) ? "true" : "false";
                    else if (value is IFormattable) text = ((IFormattable)value).ToString(null, CultureInfo.InvariantCulture);
                    else text = value.ToString();
                    fields[i] = Quote(text);
                }
                output.WriteLine(string.Join(",", fields));
                count++;
            }
        }
        return count;
    }
}
