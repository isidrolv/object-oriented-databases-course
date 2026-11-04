# Lección 00 · Cómo estudiar este libro

## Objetivos

- Entender por qué el método de este curso acelera el aprendizaje.
- Montar tu sistema de tarjetas y tu registro de progreso antes del día 1.
- Conocer la estructura de cada lección.

## Explícalo como Feynman

!!! quote "Versión para un niño de 12 años"
    Tu cerebro es como un bosque. Cada vez que **recuerdas** algo sin mirar, pisas un sendero y lo vuelves más ancho. Si solo lees, miras el sendero desde un helicóptero: parece fácil, pero no lo pisaste. Si vuelves a pisarlo justo cuando la hierba empieza a crecer (repetición espaciada), el sendero se vuelve un camino. Y si alternas varios senderos (intercalación), aprendes a elegir el camino correcto en cada cruce.

## 1. La ciencia en cinco ideas

1. **Efecto de prueba (*testing effect*).** Recuperar información produce más retención que volver a estudiarla. Roediger y Karpicke (2006) mostraron que los estudiantes que se autoevaluaron recordaban más una semana después que los que releyeron, aunque estos últimos se sentían más seguros.
2. **Curva del olvido.** Ebbinghaus (1885): sin repaso olvidamos rápido (gran parte en las primeras 24–48 h). Cada repaso bien espaciado aplana la curva.
3. **Dificultades deseables.** Bjork: lo que hace el estudio más difícil a corto plazo (mezclar temas, espaciar, autoevaluarse) mejora la retención a largo plazo.
4. **Intercalación.** Mezclar tipos de problema obliga a identificar *qué* estrategia usar; practicar en bloques solo entrena *cómo* aplicarla.
5. **Elaboración y generación.** Explicar con tus propias palabras y generar ejemplos crea más conexiones que leer ejemplos ajenos.

## 2. Estructura de cada lección

| Sección | Para qué sirve |
|---|---|
| Objetivos | Saber qué debes poder hacer al final |
| Explícalo como Feynman | Modelo de explicación simple; compárala con la tuya |
| Contenido | Teoría con profundidad de posgrado |
| Ejemplos | Código y escenarios que muestran cada concepto |
| Errores comunes | Ideas falsas típicas, también en entrevistas |
| Conexiones (intercalación) | Vínculos con otras lecciones para mezclar temas |
| Preguntas de recuerdo activo | Responde **antes** de abrir la respuesta |
| Tarjetas de repaso | Pares pregunta/respuesta para tu sistema espaciado |

## 3. Tu sistema de tarjetas

Puedes usar Anki, Mochi, RemNote o tarjetas de papel con el **sistema Leitner**:

```text
Caja 1: diario      ← toda tarjeta nueva o fallada
Caja 2: cada 3 días
Caja 3: semanal
Caja 4: cada 2 semanas
Caja 5: mensual     → si aciertas aquí, la tarjeta está "dominada"
```

Formato recomendado de tarjeta: **una sola idea**, pregunta precisa, respuesta corta y un ejemplo.

```text
FRENTE:  ¿Qué problema resuelve la persistencia por alcanzabilidad?
REVERSO: Decidir qué guardar sin marcar cada objeto: todo objeto alcanzable
         desde una raíz persistente se vuelve persistente.
         Ej.: root['clientes'] = [c1]  → c1 y sus pedidos se guardan.
```

## 4. Preparar el entorno técnico

Para los ejemplos de código conviene tener:

```bash
# Python: ZODB, una base de datos de objetos nativa de Python
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate en Linux/macOS)
pip install ZODB

# PostgreSQL (lección 09): con Docker
docker run --name pg-oodb -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16

# Java (lecciones 05 y 10): JDK 17+ y Maven, para JPA/Hibernate u ObjectDB
```

!!! note "No necesitas todo el día 1"
    Instala ZODB en la semana 5 y PostgreSQL en la semana 9. El resto del curso es conceptual o se puede seguir leyendo el código.

## 5. Errores comunes al estudiar

- **Subrayar y releer.** Da una falsa sensación de dominio.
- **Estudiar 6 horas el domingo.** Espaciar 6 sesiones de 1 hora rinde mucho más.
- **Saltarse los ejercicios «fáciles».** La fluidez en lo básico libera memoria de trabajo para lo avanzado.
- **Mirar la respuesta demasiado pronto.** Esfuérzate al menos 60 segundos; el error seguido de retroalimentación también enseña (*hypercorrection effect*).

## Preguntas de recuerdo activo

1. ¿Por qué releer es menos eficaz que autoevaluarse?
2. ¿Qué intervalos de repaso usa este curso?
3. ¿Cuál es la diferencia entre práctica en bloques e intercalada?

??? success "Respuestas"
    1. Porque releer produce fluidez de reconocimiento, no de recuperación; la recuperación activa fortalece la memoria y revela lagunas.
    2. +1, +3, +7, +14 y +30 días.
    3. En bloques se practica un solo tipo de problema seguido; intercalada mezcla tipos y obliga a elegir la estrategia, lo que mejora la transferencia.

## Tarjetas de repaso

| Frente | Reverso |
|---|---|
| ¿Qué es el *testing effect*? | Recuperar información mejora la retención más que volver a estudiarla |
| ¿Qué es una dificultad deseable? | Un obstáculo de corto plazo (espaciar, mezclar, autoevaluarse) que mejora la memoria a largo plazo |
| Pasos de la técnica Feynman | Elegir concepto → explicarlo simple → detectar lagunas → volver a la fuente → simplificar con analogías |
