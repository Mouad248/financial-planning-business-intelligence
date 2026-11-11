let
    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WMlSKjQUA", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Placeholder = _t]),
    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Placeholder", Int64.Type}})
in
    #"Changed Type"