from app.tools.adicionar_evento import executar_adicionar_evento
from app.tools.adicionar_tarefa import executar_adicionar_tarefa
from app.tools.buscar_material_rag import executar_buscar_material_rag
from app.tools.concluir_tarefa import executar_concluir_tarefa
from app.tools.consultar_agenda import executar_consultar_agenda
from app.tools.listar_tarefas import executar_listar_tarefas

TOOLS_REGISTRY: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "adicionar_evento",
            "description": (
                "Adiciona um novo evento à agenda acadêmica do estudante. "
                "Use quando o usuário quiser registrar algo que ACONTECE em data e hora "
                "específicas: aulas, provas, reuniões, prazos de entrega com horário. "
                "NÃO use para tarefas a fazer sem hora definida — use adicionar_tarefa."
            ),
            "parameters": {
                "type": "object",
                "required": ["titulo", "data", "tipo"],
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Nome do evento. Ex: 'Aula de IA', 'Prova de Cálculo'.",
                    },
                    "data": {
                        "type": "string",
                        "description": "Data no formato YYYY-MM-DD. Ex: '2026-06-15'.",
                    },
                    "hora_inicio": {
                        "type": "string",
                        "description": "Horário de início no formato HH:MM. Ex: '14:00'. Opcional.",
                    },
                    "hora_fim": {
                        "type": "string",
                        "description": "Horário de fim no formato HH:MM. Ex: '16:00'. Opcional.",
                    },
                    "tipo": {
                        "type": "string",
                        "enum": ["aula", "prova", "prazo", "outro"],
                        "description": "Tipo do evento.",
                    },
                    "local": {
                        "type": "string",
                        "description": "Local do evento. Ex: 'Sala B-204', 'Google Meet'. Opcional.",
                    },
                    "descricao": {
                        "type": "string",
                        "description": "Descrição adicional. Opcional.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_agenda",
            "description": (
                "Consulta eventos da agenda acadêmica. Use quando o usuário perguntar sobre "
                "aulas, provas, compromissos ou o que tem em um período específico. "
                "Exemplos: 'o que tenho hoje?', 'tenho prova amanhã?', 'quais minhas aulas esta semana?'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "periodo": {
                        "type": "string",
                        "enum": ["hoje", "amanha", "semana", "mes"],
                        "description": (
                            "Período relativo de consulta. 'hoje' = dia atual, "
                            "'amanha' = próximo dia, 'semana' = próximos 7 dias, "
                            "'mes' = próximos 30 dias."
                        ),
                    },
                    "data_inicio": {
                        "type": "string",
                        "description": "Data de início no formato YYYY-MM-DD. Ignorado se 'periodo' for informado.",
                    },
                    "data_fim": {
                        "type": "string",
                        "description": "Data de fim no formato YYYY-MM-DD. Opcional. Usado com 'data_inicio' para intervalos customizados.",
                    },
                },
                "oneOf": [{"required": ["periodo"]}, {"required": ["data_inicio"]}],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_tarefas",
            "description": (
                "Lista tarefas do estudante. Use quando o usuário perguntar o que tem para fazer, "
                "quais tarefas estão pendentes ou concluídas. "
                "Exemplos: 'o que tenho que fazer?', 'quais tarefas de IA faltam?', 'mostra minhas tarefas concluídas'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pendente", "concluida", "todas"],
                        "default": "pendente",
                        "description": "'pendente' retorna apenas não concluídas, 'concluida' apenas concluídas, 'todas' retorna ambas.",
                    },
                    "disciplina": {
                        "type": "string",
                        "description": "Filtrar por disciplina específica. Opcional. Ex: 'Inteligência Artificial'. Se omitido, retorna de todas.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adicionar_tarefa",
            "description": (
                "Adiciona uma nova tarefa à lista do estudante. Use quando o usuário pedir para "
                "registrar algo a fazer, criar um lembrete acadêmico ou adicionar uma atividade. "
                "Exemplos: 'adiciona uma tarefa para estudar capítulo 3', 'cria um lembrete para entregar o trabalho'."
            ),
            "parameters": {
                "type": "object",
                "required": ["titulo"],
                "properties": {
                    "titulo": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 200,
                        "description": "Título obrigatório da tarefa. Ex: 'Estudar regressão logística'.",
                    },
                    "descricao": {
                        "type": "string",
                        "maxLength": 1000,
                        "description": "Descrição detalhada. Opcional.",
                    },
                    "disciplina": {
                        "type": "string",
                        "maxLength": 100,
                        "description": "Disciplina relacionada. Opcional. Ex: 'Inteligência Artificial'.",
                    },
                    "prazo": {
                        "type": "string",
                        "description": "Data limite no formato YYYY-MM-DD. Opcional.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "concluir_tarefa",
            "description": (
                "Marca uma tarefa como concluída. Use quando o usuário disser que terminou uma tarefa. "
                "Se o UUID não for conhecido, chame listar_tarefas primeiro para obtê-lo."
            ),
            "parameters": {
                "type": "object",
                "required": ["tarefa_id"],
                "properties": {
                    "tarefa_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "UUID da tarefa a ser marcada como concluída. Obtenha via listar_tarefas se necessário.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_material_rag",
            "description": (
                "Busca trechos de materiais de estudo usando RAG. Use quando o usuário fizer perguntas "
                "sobre conteúdo acadêmico, conceitos ou teorias. "
                "Exemplos: 'explique regressão logística', 'o que são embeddings?', 'resuma redes neurais'."
            ),
            "parameters": {
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 500,
                        "description": "Pergunta ou tema a ser buscado. Ex: 'regressão logística'.",
                    },
                    "top_k": {
                        "type": "integer",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                        "description": "Número máximo de chunks a retornar. Use 3-5 para respostas objetivas, 10-15 para análises abrangentes.",
                    },
                    "documento": {
                        "type": "string",
                        "description": "Nome do arquivo para filtrar a busca. Opcional. Ex: 'apostila_ia_01.pdf'. Se omitido, busca em todos.",
                    },
                    "threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.0,
                        "description": "Score mínimo de similaridade. 0.0 = sem filtro. Use 0.5-0.7 para filtrar resultados pouco relevantes.",
                    },
                },
            },
        },
    },
]

TOOLS_EXECUTORES: dict = {
    "adicionar_evento": executar_adicionar_evento,
    "consultar_agenda": executar_consultar_agenda,
    "listar_tarefas": executar_listar_tarefas,
    "adicionar_tarefa": executar_adicionar_tarefa,
    "concluir_tarefa": executar_concluir_tarefa,
    "buscar_material_rag": executar_buscar_material_rag,
}

TOOLS_DISPATCH = TOOLS_EXECUTORES
