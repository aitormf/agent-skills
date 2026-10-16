# Informe: servidor de LLM local para ~20 usuarios

**Fecha:** 7 de octubre de 2026
**Hardware objetivo:** Mini PC AMD Ryzen AI MAX+ 395 · 128 GB LPDDR5X · SSD 2 TB PCIe 4.0
**Motores evaluados:** Ollama, llama.cpp y vLLM

---

## Resumen ejecutivo

**Recomendación: llama.cpp (`llama-server`) con el backend Vulkan, sobre Linux, sirviendo un modelo MoE (Qwen3.6-35B-A3B como modelo por defecto).** Delante, Open WebUI para los usuarios y, opcionalmente, LiteLLM como pasarela de API.

- En GPUs NVIDIA, vLLM sería la opción natural a partir de 3–5 usuarios simultáneos. **En este hardware no:** su soporte en la iGPU gfx1151 aún no está maduro, escala mal con modelos grandes y exige mucho mantenimiento.
- El límite real del equipo es el **ancho de banda de memoria (~256 GB/s)**, no la capacidad. Por eso conviene usar modelos MoE con pocos parámetros activos.
- Rendimiento esperado: **~20–35 tok/s por usuario** en horas punta de uso tipo chat. El punto débil son los prompts muy largos (RAG pesado, agentes de código).

---

## Parte 1: Ollama vs llama.cpp vs vLLM (comparativa general)

### 1.1 Qué es cada uno

| | **llama.cpp** | **Ollama** | **vLLM** |
|---|---|---|---|
| Qué es | Motor de inferencia en C/C++ (formato GGUF) con servidor `llama-server` | Envoltorio en Go con gestión de modelos. Usa llama.cpp en x86/NVIDIA/AMD y **MLX en Apple Silicon** (desde la v0.19, marzo 2026) | Servidor de inferencia en Python/PyTorch para producción, con PagedAttention y *continuous batching* |
| Para quién | Quien quiere control y rendimiento máximos en un único equipo | Desarrolladores y uso local con el mínimo esfuerzo | Equipos que sirven a muchos usuarios a la vez |
| Hardware | CPU, CUDA, ROCm, Metal, Vulkan, ARM, embebidos | CPU, NVIDIA, AMD y Apple Silicon | Sobre todo NVIDIA CUDA. AMD está incompleto. Hay backend CPU y, desde sept. 2026, `vllm-metal` para Mac |
| Versión (oct. 2026) | Builds diarias (b11459) y versiones numeradas v0.6.0 | v0.35.x (hay una v0.40 en rc) | v0.30.0 (22 sept. 2026) |

### 1.2 Facilidad de uso

**Ollama: ⭐⭐⭐⭐⭐**
- Instalas, ejecutas `ollama run modelo` y ya funciona. Descarga los modelos solo, elige la cuantización y carga o descarga los modelos según la demanda.
- Trae API compatible con OpenAI y está integrado con casi todo: Open WebUI, LangChain, IDEs, n8n…
- La pega es que esconde parámetros. Para afinar contexto, capas en la GPU, etc., tienes que usar Modelfiles o variables de entorno.

**llama.cpp: ⭐⭐⭐**
- Hay binarios precompilados, pero tienes que buscar el GGUF tú mismo, elegir la cuantización y ajustar los flags (`-ngl`, `-c`, `-np`, etc.).
- Ha mejorado mucho. Desde diciembre de 2025 tiene **router mode**: un único endpoint para todos tus modelos, carga bajo demanda y descarta el menos usado (LRU). También tiene ficheros de presets, interfaz web y endpoints de OpenAI y Anthropic.
- Ojo con el router: por defecto permite hasta 4 modelos a la vez, y eso no cabe en una GPU de 24 GB. Se recomienda `--models-max 1` si solo tienes una GPU.

**vLLM: ⭐⭐**
- Requiere un entorno Python o Docker, drivers CUDA compatibles y conocer bien los parámetros (`--gpu-memory-utilization`, `--max-model-len`, tensor parallel…).
- Usa modelos de Hugging Face (FP16, AWQ, GPTQ, FP8). El soporte de GGUF es secundario.
- Está pensado para desplegar en servidores o Kubernetes, no para usar "en el portátil".

### 1.3 Consumo de recursos y rendimiento

**Un solo usuario.** Los tres van parecidos. Ejemplo con Llama 3.1 8B: Ollama ~62 tok/s, llama.cpp ~65 tok/s y vLLM ~71 tok/s. Buena parte de la diferencia se debe a la cuantización, no al motor.
- Lo que cuesta la capa de Ollama sobre llama.cpp cambia mucho según el hardware. Las mediciones van desde ~2 % (RTX 5090) a 10–19 % (RTX 5060 Ti / 4090), y hasta ~50 % en una L40S con el mismo GGUF.
- Con los mismos pesos en 4 bits, los kernels Marlin de vLLM sacan un 9–12 % más que llama.cpp.

**Muchos usuarios a la vez.** Aquí vLLM gana con claridad (en NVIDIA):
- Con 50 usuarios: Ollama ~155 tok/s frente a ~920 tok/s de vLLM. La latencia p99 es de ~24,7 s frente a ~2,8 s.
- vLLM rinde unas 10–20× más con alta concurrencia y unas 2,3× con 8 usuarios.

**Memoria:**

| | Ollama / llama.cpp | vLLM |
|---|---|---|
| VRAM en reposo (8B) | ~5,2 GB (Q4_K_M) | ~16,1 GB (FP16) / ~12 GB (AWQ) |
| Política de VRAM | Reserva solo los pesos y el KV cache del contexto que usas | **Reserva de entrada ~90 % de la GPU** para el KV cache (ajustable con `--gpu-memory-utilization`) |
| RAM del sistema | ~1,8 GB | ~4,6 GB (runtime de Python, tokenizer, scheduler) |
| Fragmentación del KV cache | 30–50 % por defecto | <4 % (PagedAttention) |

En la práctica:
- llama.cpp es el que mejor aprovecha **CPU, poca VRAM o el reparto entre CPU y GPU** (offload parcial de capas).
- Ollama consume casi lo mismo que llama.cpp y lo hace transparente.
- vLLM monopoliza la GPU, pero a cambio saca el máximo rendimiento por GPU cuando hay concurrencia.
- En Apple Silicon, Ollama con MLX y `vllm-metal` superan claramente a llama.cpp sobre Metal (se citan entre 1,4 y 1,8× para MLX).

### 1.4 Mantenimiento

**Ollama: bajo**
- Se actualiza con el gestor de paquetes o el instalador, y gestiona modelos y almacenamiento por ti.
- Integra solo las mejoras de llama.cpp y MLX (por ejemplo, la v0.35.1 subió llama.cpp a b11232). Eso sí, las incorpora **con algo de retraso** respecto a llama.cpp.
- Riesgo: depende de las decisiones de una empresa (sus cambios de motor, de formato del registro de modelos, etc.).

**llama.cpp: medio**
- Saca builds casi a diario (más de 170 solo en abril de 2026). Conviene **fijar una versión**: para servidores, las numeradas v0.x; para estar a la última, las bNNNN.
- Mantienes tú los GGUF, los flags y los servicios systemd. Si actualizas a menudo, de vez en cuando cambian flags o hay regresiones.
- Tiene pocas dependencias: es un binario que puedes compilar sin más. Muy estable en producción si no lo tocas.

**vLLM: alto**
- Saca una versión cada 2–3 semanas y suele romper cosas (la v0.30 dejó obsoletos el modo de caché de Mamba y el entrypoint de gRPC, y cambió YaRN).
- Arrastra la matriz de compatibilidad CUDA, driver, PyTorch y versión de Python. Lo normal es usar la imagen Docker oficial y fijar la versión.
- A cambio tiene un ecosistema de producción maduro: métricas Prometheus, multi-GPU, multi-nodo y caché de pesos en GPU para reiniciar rápido (v0.30).

### 1.5 Matriz resumen

| Criterio | Ollama | llama.cpp | vLLM |
|---|---|---|---|
| Facilidad de uso | 🟢 Muy alta | 🟡 Media | 🔴 Baja |
| Rendimiento con 1 usuario | 🟡 Bueno (con algo de overhead) | 🟢 Muy bueno | 🟢 Muy bueno |
| Rendimiento con muchos usuarios | 🔴 Pobre | 🟡 Aceptable (`-np`) | 🟢 Excelente (en NVIDIA) |
| Consumo de VRAM | 🟢 Bajo | 🟢 Mínimo | 🔴 Alto (reserva por adelantado) |
| CPU sin GPU | 🟢 Sí | 🟢 El mejor | 🟡 Posible, pero no es su terreno |
| Variedad de hardware | 🟢 Amplia | 🟢 La más amplia | 🔴 Centrado en NVIDIA |
| Mantenimiento | 🟢 Bajo | 🟡 Medio | 🔴 Alto |
| Producción a escala | 🔴 | 🟡 | 🟢 |

**Regla general:**
- **Prototipos, uso personal o equipo pequeño, y Mac:** Ollama.
- **Un solo servidor modesto (CPU o GPU pequeña), control fino, o un servicio interno con pocos usuarios:** llama.cpp.
- **Más de 3–5 usuarios simultáneos, con GPUs NVIDIA dedicadas:** vLLM.

---

## Parte 2: recomendación para el Ryzen AI MAX+ 395 con ~20 usuarios

### 2.1 Por qué este hardware cambia la elección

**1. La memoria es grande pero lenta.** Tenéis 128 GB unificados, con unos 110–120 GB utilizables por la GPU integrada (Radeon 8060S, gfx1151). Eso permite cargar modelos muy grandes, pero el ancho de banda es de unos **256 GB/s**, 4–7 veces menos que una GPU dedicada de gama alta. La velocidad de generación depende directamente de ese ancho de banda, así que encaja con **modelos MoE de pocos parámetros activos**:

| Modelo | Memoria | 1 usuario (tok/s) | Uso |
|---|---|---|---|
| Qwen3.6-35B-A3B (Q4_K_M) | ~21 GB | ~60 (Vulkan) | **El mejor para concurrencia** |
| gpt-oss-20B | ~11 GB | ~80 | Rápido y ligero |
| gpt-oss-120B (MXFP4) | ~59 GB | ~55 | Más calidad, pero menos margen con varios usuarios |
| Qwen3-235B-A22B | ~130 GB | 8–11 | ❌ Demasiado lento para 20 usuarios |
| Modelos densos de 70B | ~40 GB | ~5 | ❌ Descartados |

**2. vLLM aún no está maduro en gfx1151:**
- ROCm 7.x ha tenido regresiones serias en este chip.
- Hay casos documentados de vLLM ejecutando gpt-oss-120B **en la CPU** (5,6 tok/s) sin avisar.
- Con modelos grandes casi no escala: Qwen3.5-122B pasó de 10,3 tok/s con 1 cliente a 16,2 tok/s con 2. Con 1 cliente llama.cpp le gana (13,6 frente a 10,3 tok/s).
- Mantenerlo exige casar versiones concretas de ROCm, PyTorch y vLLM, o usar *toolboxes* de la comunidad. Es el "mantenimiento alto" de la Parte 1, multiplicado.

**3. llama.cpp con Vulkan es la opción más estable y rápida en este chip.** Genera un 10–20 % más rápido que ROCm/HIP y funciona con los drivers estándar de Mesa (RADV). Con varios *slots* en paralelo escala de forma razonable:

| Qwen3.5/3.6-35B-A3B | Rendimiento total | Por usuario |
|---|---|---|
| 1 petición | ~45–60 tok/s | ~45–60 |
| 4 en paralelo | ~130 tok/s | ~33 |
| 8 en paralelo | ~120–146 tok/s | ~15–18 |
| 16 en paralelo | ~113–168 tok/s (con regresiones) | ~7–10 |

### 2.2 Qué significa con 20 usuarios

No estarán los 20 generando a la vez. En uso de chat normal suele haber **3–6 peticiones simultáneas**:

- **Chat, consultas y redacción:** ✅ va bien. Con Qwen3.6-35B-A3B, cada usuario tendrá unos 20–35 tok/s en horas punta, más rápido de lo que se lee.
- **Agentes de código, RAG con documentos largos o automatizaciones en lote:** ⚠️ es el punto débil. El *prefill* (procesar el prompt) va a ~1.000 tok/s, así que un prompt de 30.000 tokens tarda unos 30 s **y bloquea a los demás mientras tanto**. Si ese es el uso principal, el equipo se quedará corto.

### 2.3 Arquitectura propuesta

```
Usuarios ──► Open WebUI (login, historial)  ─┐
Apps/n8n ──► LiteLLM (API keys, límites)    ─┴─► llama-server (Vulkan, router mode)
                                                   ├─ Qwen3.6-35B-A3B  (por defecto)
                                                   └─ gpt-oss-120B     (bajo demanda, opcional)
```

- **Open WebUI** da una interfaz tipo ChatGPT con usuarios y autenticación.
- **LiteLLM**, opcional, pone claves por usuario o aplicación, límites de uso y registros. También permite **cambiar de motor** (por ejemplo, a vLLM cuando madure en gfx1151) sin tocar los clientes.

### 2.4 Configuración clave

1. **Sistema operativo:** Linux (Ubuntu 24.04 o Fedora) con un kernel y Mesa recientes. En Windows, Ollama recurre a la CPU por defecto en este chip.
2. **Memoria para la GPU:** dejad poca memoria fija para la GPU en la BIOS y ampliad la memoria dinámica (GTT) con parámetros del kernel, para que la GPU pueda usar unos 110–120 GB.
3. **Arranque de llama-server** (como punto de partida, ajustadlo midiendo):

   ```bash
   # 8 slots x 16k de contexto cada uno; --cache-reuse reutiliza el prompt común (system prompt)
   llama-server -m Qwen3.6-35B-A3B-Q4_K_M.gguf \
     -ngl 999 -fa on \
     -np 8 -c 131072 \
     --cache-reuse 256 \
     --host 0.0.0.0 --port 8080 --metrics
   ```

   - El contexto **se reparte entre los slots**: con `-c 131072` y `-np 8` cada usuario tiene 16k. Subid `-c` si necesitáis más; memoria sobra.
   - Empezad con `-np 8`. Con 16 se han medido regresiones en modelos MoE.
   - En router mode con varios modelos, poned `--models-max 2` como máximo.
4. **Fijad la versión** de llama.cpp (las numeradas v0.x) y del driver Mesa. Antes de actualizar, probad la nueva en un segundo puerto: con ROCm y Mesa hay regresiones frecuentes en este chip.

### 2.5 ¿Y Ollama?

Es válido para un **piloto rápido** (`OLLAMA_VULKAN=1`, `OLLAMA_NUM_PARALLEL=8`), pero tiene tres desventajas aquí:
- El soporte de ROCm para gfx1151 no es estable en las versiones oficiales.
- Añade una sobrecarga variable sobre llama.cpp.
- Da menos control sobre los slots, el contexto y la caché, que es justo lo que importa con 20 usuarios.

Se puede empezar con Ollama una semana para validar los casos de uso y luego pasar a llama-server.

### 2.6 Riesgos y plan B

- **Si se queda corto** (muchos agentes o RAG pesado): no hace falta más memoria, sino más ancho de banda. Las opciones son un segundo equipo igual detrás de LiteLLM (balanceo sencillo) o una GPU NVIDIA dedicada con vLLM para la carga concurrente.
- **Medid antes de comprometeros.** Lanzad `llama-bench` y una prueba de carga con 8–10 clientes simultáneos con vuestros prompts reales. Las cifras públicas cambian mucho según la versión de llama.cpp, Mesa y ROCm.

> **Aviso:** las cifras de benchmarks cambian mucho entre fuentes según el hardware, la cuantización y la versión, y algunas son incoherentes entre sí. Medid siempre con vuestro modelo y vuestra carga reales.

---

## Fuentes

### Comparativa general
- [SitePoint – Ollama vs vLLM: Performance Benchmark 2026](https://www.sitepoint.com/ollama-vs-vllm-performance-benchmark-2026/)
- [DEV – Ollama vs llama.cpp vs vLLM 2026](https://dev.to/thurmon_demich/ollama-vs-llamacpp-vs-vllm-which-should-you-use-in-2026-10gp)
- [ComputingForGeeks – Speed Benchmarked](https://computingforgeeks.com/ollama-vs-vllm-vs-llama-cpp/)
- [InsiderLLM – One User vs Many](https://insiderllm.com/guides/llamacpp-vs-ollama-vs-vllm/)
- [PromptQuorum – Speed, Batching & GPU Benchmarks](https://www.promptquorum.com/local-llms/llamacpp-vs-ollama-vs-vllm)
- [D-Central – Local Inference Server Comparison](https://d-central.tech/ollama-vs-vllm-vs-llama-cpp/)
- [Codersera – Ollama vs LM Studio vs vLLM vs llama.cpp vs MLX 2026](https://codersera.com/blog/ollama-vs-lm-studio-vs-vllm-vs-llama-cpp-vs-mlx-2026/)
- [yage.ai – MLX vs llama.cpp y por qué Ollama cambió](https://yage.ai/share/mlx-apple-silicon-en-20260331.html)
- [Angelo Lima – Ollama in 2026](https://angelo-lima.fr/en/ollama-2026-state-of-the-art-en/)
- [Ollama Blog](https://ollama.com/blog) · [Releasebot – Ollama](https://releasebot.io/updates/ollama)
- [vLLM v0.30.0 release](https://github.com/vllm-project/vllm/releases/tag/v0.30.0) · [vllm-metal announcement](https://vllm.ai/blog/2026-09-22-vllm-metal-v0-28-0) · [vLLM Installation docs](https://docs.vllm.ai/en/latest/getting_started/installation/)
- [Hugging Face – Model Management in llama.cpp](https://huggingface.co/blog/ggml-org/model-management-in-llamacpp)
- [runaihome – llama.cpp Router Mode 2026](https://runaihome.com/blog/llama-server-router-mode-multi-model-setup-2026/)
- [Fazm – llama.cpp Releases April 2026](https://fazm.ai/blog/llama-cpp-release-april-2026)
- [freedom.tech – llama.cpp release history](https://freedom.tech/project/llama-cpp/)
- [SSD Nodes – Pin llama.cpp releases](https://www.ssdnodes.com/learn/pin-llama-cpp-releases-on-a-server)

### Strix Halo / Ryzen AI MAX+ 395
- [Soot/Silicon – SGLang vs vLLM: Strix Halo benchmarks (ago. 2026)](https://www.soothill.io/blog/2026/08/10/sglang-vllm-llamacpp-evox3/)
- [Soot/Silicon – Strix Halo LLM upgrade: wins and regressions](https://www.soothill.io/blog/2026/08/11/strix-halo-llm-stack-upgrade-benchmarks/)
- [llama.cpp Discussion #20856 – Known-Good Strix Halo ROCm + llama.cpp Stack](https://github.com/ggml-org/llama.cpp/discussions/20856)
- [vllm-omni PR #6236 – ROCm validation on gfx1151](https://github.com/vllm-project/vllm-omni/pull/6236)
- [llm-tracker – Strix Halo](https://llm-tracker.info/_TOORG/Strix-Halo)
- [Framework Community – Strix Halo GPU LLM Performance Tests](https://community.frame.work/t/amd-strix-halo-ryzen-ai-max-395-gpu-llm-performance-tests/72521)
- [Zenn – Local LLM Performance Improved on Ryzen AI Max+ 395](https://zenn.dev/shuzan/articles/72852bb9621b40?locale=en)
- [Zenn – The 9-Month Hell of Running Local LLMs on Ryzen AI Max+ 395](https://zenn.dev/shuzan/articles/0605b909fb23e4?locale=en)
- [MindStudio – GPT-OSS, Qwen3.6 and Hermes on 128GB Unified Memory](https://www.mindstudio.ai/blog/local-llm-benchmarks-ryzen-ai-halo)
- [Level1Techs – Strix Halo LLM Benchmark Results](https://forum.level1techs.com/t/strix-halo-ryzen-ai-max-395-llm-benchmark-results/233796)
- [nishtahir – GMKTec Evo-X2 Benchmarks](https://nishtahir.com/gmktec-evo-x2-ryzen-ai-max-395-benchmarks/)
- [strix-halo-guide – Benchmarks](https://github.com/hogeheer499-commits/strix-halo-guide/blob/main/BENCHMARKS.md) · [Setup](https://github.com/hogeheer499-commits/strix-halo-guide/blob/main/STRIX_HALO_LOCAL_LLM_SETUP.md)
- [Ollama Issue #14855 – Strix Halo ROCm Working Guide](https://github.com/ollama/ollama/issues/14855)
- [PromptQuorum – Strix Halo + Ollama Vulkan](https://www.promptquorum.com/prompt-bites/strix-halo-ollama-vulkan)
- [LocalAIMaster – Strix Halo for Local AI 2026](https://localaimaster.com/blog/strix-halo-ai-max-395-guide)
- [AMD – Ryzen AI Max+ AI PCs (2026)](https://www.amd.com/en/blogs/2026/amd-ryzen-ai-max-ai-pcs-deliver-exceptional-intelligence.html)
