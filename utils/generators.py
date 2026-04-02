def row_generator(df):
    for _, row in df.iterrows():
        yield row.to_dict()
        