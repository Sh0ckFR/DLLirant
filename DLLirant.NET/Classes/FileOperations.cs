using System;
using System.IO;

namespace DLLirant.NET.Classes
{
    internal class FileOperations
    {
        public void CreateDirectory(string path)
        {
            if (!Directory.Exists(path))
                Directory.CreateDirectory(path);
        }

        public void DeleteDirectory(string path)
        {
            if (Directory.Exists(path))
            {
                try
                {
                    Directory.Delete(path, true);
                } catch (UnauthorizedAccessException) { }
            }
        }

        public void CopyFile(string file)
        {
            if (!File.Exists($"output/{Path.GetFileName(file)}"))
            {
                File.Copy(file, $"output/{Path.GetFileName(file)}");
            }
        }

        public void RenameFile(string path, string newpath)
        {
            if (File.Exists(path))
            {
                File.Move(path, newpath);
            }
        }
    }
}
