import pandas as pd

file_path = "Ruta al archivo Excel"

df_posts = pd.read_excel(file_path, sheet_name="Posts")
df_meta = pd.read_excel(file_path, sheet_name="Metadata")

df_meta["ID_Político"] = df_meta["ID_Político"].ffill().astype(int)

conteo = df_posts.groupby("ID_Político")["Enlace_Post"].count().reset_index()
conteo.columns = ["ID_Político", "Total_Posts"]

df_twitter = df_meta[["ID_Político", "Twitter"]].drop_duplicates()

resultado = pd.merge(conteo, df_twitter, on="ID_Político", how="left")

for i in range(len(resultado)):
    print(
        f"ID {resultado.loc[i, 'ID_Político']} (@{resultado.loc[i, 'Twitter']}): {resultado.loc[i, 'Total_Posts']} posts")
