import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import json

st.set_page_config(page_title='Protótipo: Método de Moreno', layout='wide')

st.title('Protótipo Interativo — Método de Moreno para Análise Grupal')

# Sidebar: metadados do estudo
st.sidebar.header('Metadados')
study_name = st.sidebar.text_input('Nome do estudo', 'Estudo Moreno - Exemplo')
group_type = st.sidebar.selectbox('Tipo de grupo', ['Residencial', 'Laboral', 'Outro'])
date = st.sidebar.date_input('Data da coleta')

st.sidebar.markdown('---')
st.sidebar.header('Operações')
if st.sidebar.button('Salvar sessão atual como JSON'):
    # Salva o dataframe de escolhas caso exista
    if 'choices_df' in st.session_state:
        payload = {
            'meta': {'study_name': study_name, 'group_type': group_type, 'date': str(date)},
            'choices': st.session_state['choices_df'].to_dict(orient='list')
        }
        with open('moreno_session.json', 'w') as f:
            json.dump(payload, f, indent=2)
        st.sidebar.success('Arquivo moreno_session.json salvo no diretório atual.')

st.header('1) Participantes')
participants_input = st.text_area('Insira os nomes dos participantes (uma linha por participante)', 
                                  value='Alice\nBeatriz\nCarla\nDaniela\nElisa')
participants = [p.strip() for p in participants_input.splitlines() if p.strip()]
st.write(f'{len(participants)} participantes registrados.')
if len(participants) == 0:
    st.warning('Adicione pelo menos um participante para continuar.')
    st.stop()

st.header('2) Coleta de escolhas sociométricas')
st.markdown('Para cada participante, escolha (por ordem) até 5 pessoas com quem preferiria trabalhar (podem ser externas ao grupo), e até 3 pessoas dentro do grupo atual.')
choices = []
col1, col2 = st.columns([2,1])
with col1:
    st.subheader('Escolhas gerais (até 5, ordem de preferência)')
    rows = []
    for p in participants:
        vals = []
        st.markdown(f'**{p}**')
        for i in range(1,6):
            sel = st.selectbox(f'{p} - escolha geral #{i}', options=['(vazio)']+participants, key=f'gen_{p}_{i}')
            vals.append(sel if sel != '(vazio)' else '')
        rows.append([p]+vals)
    gen_df = pd.DataFrame(rows, columns=['actor','g1','g2','g3','g4','g5'])
    st.session_state['gen_df'] = gen_df

with col2:
    st.subheader('Escolhas internas (até 3 dentro do grupo)')
    rows2 = []
    for p in participants:
        vals = []
        for i in range(1,4):
            sel = st.selectbox(f'{p} - escolha interna #{i}', options=['(vazio)']+participants, key=f'int_{p}_{i}')
            vals.append(sel if sel != '(vazio)' else '')
        rows2.append([p]+vals)
    int_df = pd.DataFrame(rows2, columns=['actor','i1','i2','i3'])
    st.session_state['int_df'] = int_df

# Botão para compilar escolhas em formato de arestas (directed)
if st.button('Gerar sociograma'):
    # Construir arestas a partir das escolhas internas (priorizadas) e gerais
    edges = []
    for _, row in int_df.iterrows():
        actor = row['actor']
        for col in ['i1','i2','i3']:
            tgt = row[col]
            if tgt and tgt != actor:
                edges.append((actor, tgt, {'type':'internal'}))
    for _, row in gen_df.iterrows():
        actor = row['actor']
        for col in ['g1','g2','g3','g4','g5']:
            tgt = row[col]
            if tgt and tgt != actor:
                edges.append((actor, tgt, {'type':'general'}))

    # Montar dataframe salvo em sessão
    import pandas as pd
    if edges:
        df_edges = pd.DataFrame([(u,v,d['type']) for (u,v,d) in edges], columns=['source','target','choice_type'])
    else:
        df_edges = pd.DataFrame(columns=['source','target','choice_type'])
    st.session_state['choices_df'] = df_edges
    st.success('Sociograma gerado e armazenado na sessão.')
    st.write(df_edges)

# Visualização do sociograma
if 'choices_df' in st.session_state and not st.session_state['choices_df'].empty:
    st.header('3) Visualização do Sociograma')
    df = st.session_state['choices_df']
    G = nx.DiGraph()
    G.add_nodes_from(participants)
    for _, r in df.iterrows():
        G.add_edge(r['source'], r['target'])

    # calcular posições e desenhar
    pos = nx.spring_layout(G, seed=42)
    fig, ax = plt.subplots(figsize=(8,6))
    nx.draw_networkx_nodes(G, pos, ax=ax)
    nx.draw_networkx_labels(G, pos, ax=ax)
    nx.draw_networkx_edges(G, pos, ax=ax, arrows=True)
    ax.set_axis_off()
    st.pyplot(fig)

    # Estatísticas simples
    st.header('4) Estatísticas e detecção básica de estruturas')
    in_deg = dict(G.in_degree())
    out_deg = dict(G.out_degree())
    stats_df = pd.DataFrame({'participant': list(in_deg.keys()),
                             'in_degree': list(in_deg.values()),
                             'out_degree': list(out_deg.values())})
    st.write(stats_df.sort_values('in_degree', ascending=False))

    # Exibir isolados
    isolates = list(nx.isolates(G))
    if isolates:
        st.warning(f'Isolados detectados: {", ".join(isolates)}')

    # Detectar pares recíprocos (mutual)
    mutual = [(u,v) for u,v in G.edges() if G.has_edge(v,u) and u < v]
    if mutual:
        st.success('Pares recíprocos detectados:')
        st.write(mutual)

    # Exportar sociograma como PNG
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    st.download_button('Download do sociograma (PNG)', data=buf, file_name='sociograma.png', mime='image/png')

st.sidebar.markdown('---')
st.sidebar.caption('Protótipo rápido. Para produção, recomenda-se autenticação, armazenamento persistente e testes.')
