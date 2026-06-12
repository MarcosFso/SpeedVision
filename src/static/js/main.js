// ============================================================
// ELEMENTOS DA PAGINA
// ============================================================
const videoStream = document.getElementById("video-stream");
const overlayParado = document.getElementById("overlay-parado");
const statusBadge = document.getElementById("status-badge");

const btnIniciar = document.getElementById("btn-iniciar");
const btnParar = document.getElementById("btn-parar");
const btnAplicarLimite = document.getElementById("btn-aplicar-limite");
const inputLimite = document.getElementById("input-limite");

const statTotal = document.getElementById("stat-total");
const statComVelocidade = document.getElementById("stat-com-velocidade");
const statMedia = document.getElementById("stat-media");
const statMaior = document.getElementById("stat-maior");
const statAcima = document.getElementById("stat-acima");
const statLimiteLabel = document.getElementById("stat-limite-label");

const galeriaInfracoes = document.getElementById("galeria-infracoes");

let radarRodando = false;
let intervaloStats = null;
let intervaloGaleria = null;


// ============================================================
// CONTROLES: INICIAR / PARAR
// ============================================================
async function iniciarRadar() {
    await fetch("/api/controle/iniciar", { method: "POST" });
    radarRodando = true;
    atualizarVisualEstado();

    // Conecta o stream de video (com timestamp para evitar cache)
    videoStream.src = "/video_feed?" + Date.now();
}

async function pararRadar() {
    await fetch("/api/controle/parar", { method: "POST" });
    radarRodando = false;
    atualizarVisualEstado();

    // Para o stream
    videoStream.src = "";
}

function atualizarVisualEstado() {
    if (radarRodando) {
        overlayParado.classList.add("escondido");
        statusBadge.textContent = "AO VIVO";
        statusBadge.classList.add("ativo");
    } else {
        overlayParado.classList.remove("escondido");
        statusBadge.textContent = "PARADO";
        statusBadge.classList.remove("ativo");
    }
}

btnIniciar.addEventListener("click", iniciarRadar);
btnParar.addEventListener("click", pararRadar);


// ============================================================
// CONTROLE: LIMITE DE VELOCIDADE
// ============================================================
btnAplicarLimite.addEventListener("click", async () => {
    const valor = parseFloat(inputLimite.value);
    if (isNaN(valor) || valor < 0) {
        alert("Informe um limite de velocidade valido.");
        return;
    }

    await fetch("/api/controle/limite", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ limite: valor }),
    });

    statLimiteLabel.textContent = `Acima de ${valor} km/h`;
});


// ============================================================
// ATUALIZACAO DAS ESTATISTICAS (POLLING)
// ============================================================
async function atualizarResumo() {
    try {
        const resposta = await fetch("/api/resumo");
        const dados = await resposta.json();

        statTotal.textContent = dados.total;
        statComVelocidade.textContent = dados.com_velocidade;
        statMedia.textContent = dados.media.toFixed(1);
        statMaior.textContent = dados.maior.toFixed(1);
        statAcima.textContent = dados.acima_limite;
        statLimiteLabel.textContent = `Acima de ${dados.limite} km/h`;

        // Mantem o input de limite sincronizado quando ainda nao foi alterado pelo usuario
        if (document.activeElement !== inputLimite) {
            inputLimite.value = dados.limite;
        }

        if (dados.rodando !== radarRodando) {
            radarRodando = dados.rodando;
            atualizarVisualEstado();
            if (radarRodando && !videoStream.src) {
                videoStream.src = "/video_feed?" + Date.now();
            }
        }
    } catch (erro) {
        console.error("Erro ao buscar resumo:", erro);
    }
}


// ============================================================
// GALERIA DE INFRACOES (POLLING)
// ============================================================
async function atualizarGaleria() {
    try {
        const resposta = await fetch("/api/infracoes");
        const itens = await resposta.json();

        if (itens.length === 0) {
            galeriaInfracoes.innerHTML =
                '<p class="galeria-vazia">Nenhuma infracao registrada ainda.</p>';
            return;
        }

        galeriaInfracoes.innerHTML = itens
            .map((item) => {
                const id = item.id ?? "?";
                const velocidade = item.velocidade ?? "?";
                return `
                    <div class="card-infracao">
                        <img src="/infracoes/${item.arquivo}" alt="Infracao veiculo ${id}">
                        <div class="info">
                            Veiculo <b>#${id}</b><br>
                            Velocidade: <b>${velocidade} km/h</b>
                        </div>
                    </div>
                `;
            })
            .join("");
    } catch (erro) {
        console.error("Erro ao buscar infracoes:", erro);
    }
}


// ============================================================
// INICIALIZACAO
// ============================================================
function iniciarPolling() {
    atualizarResumo();
    atualizarGaleria();

    intervaloStats = setInterval(atualizarResumo, 1000);
    intervaloGaleria = setInterval(atualizarGaleria, 3000);
}

atualizarVisualEstado();
iniciarPolling();
