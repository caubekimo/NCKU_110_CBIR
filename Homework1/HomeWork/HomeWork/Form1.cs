using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace HomeWork
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }

        private void btnSelectTargetFolder_Click(object sender, EventArgs e)
        {
            if (this.folderBrowserDialog1.ShowDialog() == DialogResult.OK)
            {
                this.txtTargetFolder.Text = this.folderBrowserDialog1.SelectedPath;

                List<Result> results = new List<Result>();

                foreach (var p1File in new DirectoryInfo(Path.Combine(this.txtTargetFolder.Text, "_query")).GetFiles("*.jpg"))
                {
                    string p1 = p1File.FullName;

                    foreach (var p2Folder in new DirectoryInfo(this.txtTargetFolder.Text).GetDirectories().Where(x => !x.FullName.Contains("_query")))
                    {
                        foreach (var p2File in p2Folder.GetFiles("*.jpg", SearchOption.AllDirectories))
                        {
                            string resultStr = string.Empty;

                            string url = @"http://127.0.0.1:5000/ComparePics?p1=" + p1File.FullName.Replace("\\", "/")
                                + "&p2=" + p2File.FullName.Replace("\\", "/");

                            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                            request.AutomaticDecompression = DecompressionMethods.GZip;

                            using (HttpWebResponse response = (HttpWebResponse)request.GetResponse())
                            using (Stream stream = response.GetResponseStream())
                            using (StreamReader reader = new StreamReader(stream))
                            {
                                resultStr = reader.ReadToEnd();
                            }

                            JToken compareResult = JArray.Parse(resultStr)[0];
                            results.Add(new Result() { P1Name = p1File.FullName, P2Name = p2File.FullName, Type = ResultType.n1, Value = float.Parse(compareResult["n1"].ToString()) });
                            results.Add(new Result() { P1Name = p1File.FullName, P2Name = p2File.FullName, Type = ResultType.n2, Value = float.Parse(compareResult["n2"].ToString()) });
                            results.Add(new Result() { P1Name = p1File.FullName, P2Name = p2File.FullName, Type = ResultType.n3, Value = float.Parse(compareResult["n3"].ToString()) });
                            results.Add(new Result() { P1Name = p1File.FullName, P2Name = p2File.FullName, Type = ResultType.n4, Value = float.Parse(compareResult["n4"].ToString()) });
                            results.Add(new Result() { P1Name = p1File.FullName, P2Name = p2File.FullName, Type = ResultType.n5, Value = float.Parse(compareResult["n5"].ToString()) });
                        }
                    }
                }

                foreach (var p1File in new DirectoryInfo(Path.Combine(this.txtTargetFolder.Text, "_query")).GetFiles("*.jpg"))
                {
                    string p1 = p1File.FullName;
                    var n1Results = results.Where(x => x.P1Name == p1 && x.Type == ResultType.n1).OrderBy(x => x.Value).Take(5);
                    var n2Results = results.Where(x => x.P1Name == p1 && x.Type == ResultType.n2).OrderBy(x => x.Value).Take(5);
                    var n3Results = results.Where(x => x.P1Name == p1 && x.Type == ResultType.n3).OrderBy(x => x.Value).Take(5);
                    var n4Results = results.Where(x => x.P1Name == p1 && x.Type == ResultType.n4).OrderByDescending(x => x.Value).Take(5);
                    var n5Results = results.Where(x => x.P1Name == p1 && x.Type == ResultType.n5).OrderByDescending(x => x.Value).Take(5);
                }
            }
        }

    }

    enum ResultType
    {
        n1,
        n2,
        n3,
        n4,
        n5
    }

    class Result
    {
        public string P1Name { get; set; }
        public string P2Name { get; set; }
        public ResultType Type { get; set; }
        public float Value { get; set; }
    }
}