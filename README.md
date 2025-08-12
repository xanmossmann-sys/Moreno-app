# Moreno App - Análise Sociométrica Interativa

Aplicativo interativo baseado no **método de Jacob Moreno** para análise de redes sociais e grupos.

## Funcionalidades
- Cadastro de participantes
- Registro de escolhas (atração, rejeição, neutra)
- Geração automática de sociogramas
- Identificação de pares recíprocos e isolados
- Exportação de gráficos

## Tecnologias
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [NetworkX](https://networkx.org/)
- [Matplotlib](https://matplotlib.org/)

## Como rodar localmente
```bash
# Criar e ativar ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar o aplicativo
streamlit run app.py
```

## Hospedagem na Nuvem
Para rodar no **Streamlit Cloud**:
1. Crie um repositório no GitHub e envie estes arquivos.
2. Vá em https://share.streamlit.io/
3. Clique **New app**, selecione o repositório e branch.
4. Coloque `app.py` no campo Main file path.
5. Clique Deploy.

---
**Autor:** Desenvolvido com auxílio de ChatGPT
