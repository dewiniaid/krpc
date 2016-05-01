using System;
using Google.Protobuf;
using System.Linq;

namespace KRPC.Test
{
    static class TestingTools
    {
        public static string ToHexString (this byte[] data)
        {
            return BitConverter.ToString (data).Replace ("-", "").ToLower ();
        }

        public static string ToHexString (this ByteString data)
        {
            return ToHexString (data.ToByteArray ());
        }

        public static ByteString ToByteString (this string data)
        {
            return ByteString.CopyFrom (
                Enumerable.Range (0, data.Length)
                .Where (x => x % 2 == 0)
                .Select (x => Convert.ToByte (data.Substring (x, 2), 16))
                .ToArray ());
        }
    }
}
