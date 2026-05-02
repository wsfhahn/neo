from rich import print
from app.common.chats import Chat, ChatMessage


test_chat = Chat(
    complete=False,
    messages=[
        ChatMessage(
            role="user",
            content="Can you please write an essay about Einstein's contributions to quantum theory? Target 5 paragraphs."
        ),
        ChatMessage(
            role="assistant",
            content="""**The Architect of Uncertainty: Albert Einstein’s Contributions to Quantum Theory**

While Albert Einstein is most famously celebrated for his theory of relativity, his foundational contributions to quantum mechanics were equally revolutionary. In the early 20th century, classical physics struggled to explain the behavior of light and energy at the atomic level. Einstein stepped into this void, providing the mathematical and conceptual frameworks that challenged the long-held belief that energy was a continuous wave. By introducing the idea of quantization, Einstein did not merely contribute to a new field; he helped ignite the revolution that would redefine our understanding of the universe.

Einstein’s first major breakthrough in this realm came in 1905 with his explanation of the photoelectric effect. Classical physics suggested that light traveled strictly as a wave, meaning its intensity should dictate the energy of electrons ejected from a metal surface. However, experiments showed that light frequency, not intensity, was the deciding factor. Einstein proposed that light is composed of discrete packets of energy, which we now call "photons." This concept of light behaving as both a particle and a wave—wave-particle duality—was a radical departure from tradition and earned him the Nobel Prize in Physics.

Beyond the nature of light, Einstein also made significant strides in understanding the statistical nature of matter. In 1924, he extended the work of Satyendra Nath Bose to describe the behavior of particles with integer spin, known as bosons. This collaboration led to the development of Bose-Einstein statistics, which describes how these particles occupy energy states. This work laid the groundwork for the discovery of the Bose-Einstein Condensate, a unique state of matter that occurs at temperatures near absolute zero, where atoms begin to act as a single quantum entity.

Despite being a founding father of the field, Einstein famously maintained a complex and often contentious relationship with the direction quantum theory took in its maturity. As the "Copenhagen Interpretation" gained dominance, led by Niels Bohr, it embraced the idea that the universe is fundamentally probabilistic and governed by uncertainty. Einstein, a staunch believer in determinism and objective reality, found this unacceptable. His famous critique, "God does not play dice with the universe," was not a dismissal of quantum mechanics itself, but a protest against the idea that physical laws were based on chance rather than underlying, hidden certainties.

In conclusion, Albert Einstein’s legacy in quantum theory is a study in contradictions. He provided the essential spark with his work on photons and Bose-Einstein statistics, yet he spent his later years questioning the very randomness those theories implied. While he may not have embraced the probabilistic nature of the subatomic world, his intellectual rigor forced the scientific community to refine its arguments and deepen its understanding. Ultimately, Einstein’s contributions ensured that quantum mechanics would become the most successful, albeit most mysterious, framework in the history of science."""
        ),
        ChatMessage(
            role="user",
            content="Can you write another one in a similar style about Niels Bohr?"
        ),
        ChatMessage(
            role="assistant",
            content="""**The Architect of the Atom: Niels Bohr’s Revolution in Quantum Mechanics**

If Albert Einstein provided the spark that ignited the quantum revolution, Niels Bohr was the master architect who built its most enduring structures. While Einstein’s work often focused on the discrete nature of light, Bohr turned his attention to the internal architecture of the atom itself. At a time when the classical model of the atom was collapsing under the weight of new experimental evidence, Bohr proposed a radical new way of visualizing the subatomic world. His work did more than just explain the atom; it established the conceptual language that would define the quantum era.

Bohr’s most significant breakthrough came in 1913 with his model of the atom, which sought to reconcile the stability of matter with the laws of physics. According to classical theory, an electron orbiting a nucleus should constantly lose energy and spiral inward, causing the atom to collapse. Bohr bypassed this impossibility by proposing that electrons exist in "stationary states"—specific, quantized orbits where they can exist without radiating energy. He argued that electrons could only move between these orbits by absorbing or emitting specific amounts of energy, a concept that perfectly explained the discrete spectral lines emitted by elements. This was a monumental leap, as it introduced the idea that at the atomic level, nature operates in jumps rather than smooth transitions.

As the field of quantum mechanics matured, Bohr became the primary defender and developer of the "Copenhagen Interpretation." This framework, developed alongside Werner Heisenberg, suggested that the subatomic world is not governed by certainty, but by probability. Bohr argued that we cannot speak of a particle’s properties, such as its position or momentum, until we actually measure them. This concept of "complementarity"—the idea that objects possess contradictory properties, such as being both a wave and a particle, depending on how they are observed—became the cornerstone of modern quantum philosophy. To Bohr, the observer and the observed were inextricably linked.

This philosophical stance placed Bohr at the center of the most famous intellectual rivalry in scientific history: his debates with Albert Einstein. While Einstein sought a deterministic universe where everything could be known with absolute precision, Bohr insisted that uncertainty was a fundamental feature of reality. Their correspondence was not merely a clash of egos, but a profound dialogue regarding the very nature of existence. Bohr’s ability to defend the probabilistic nature of the universe against the world’s greatest mind helped solidify the Copenhagen Interpretation as the standard view of quantum mechanics for decades.

In conclusion, Niels Bohr was the guiding light of the quantum revolution, providing both the mathematical models and the philosophical depth required to understand the microscopic world. Through his quantized atom and his principle of complementarity, he transformed physics from a study of predictable certainties into a study of profound possibilities. While Einstein’s contributions were characterized by a quest for underlying order, Bohr’s legacy lies in his courage to embrace the inherent mystery and complexity of the quantum realm."""
        ),
        ChatMessage(
            role="user",
            content="Now, can you write some key takeaways about this whole conversation?"
        ),
        ChatMessage(
            role="assistant",
            content="""Here are the key takeaways from our exploration of the two giants of quantum physics:

### 1. The "Spark" vs. The "Architect"
The conversation highlights a fundamental distinction in how scientific revolutions happen. **Einstein** acted as the catalyst; his work on the photoelectric effect provided the "spark" by proving that energy is quantized (packets of light). **Bohr** acted as the architect; he took those raw concepts and built a structural model of the atom, creating the framework that allowed the field to grow into a cohesive discipline.

### 2. Complementary Scientific Roles
The two men represented two different, yet equally necessary, modes of scientific inquiry:
* **Einstein** focused on the **physical properties** of light and matter (photons and bosons), seeking to find the underlying, objective rules of the universe.
* **Bohr** focused on the **behavior and observation** of the atom, seeking to understand how the act of measurement defines what we can actually know about reality.

### 3. The Great Philosophical Divide: Determinism vs. Probability
The core of the "quantum debate" was not about whether the math worked (both men agreed it did), but about what the math *meant*:
* **Einstein (Determinism):** Believed the universe is predictable and that "hidden variables" must exist. He believed that if we had enough data, we could eliminate chance.
* **Bohr (Probabilism):** Believed that uncertainty is not a lack of data, but a fundamental property of nature. To Bohr, the universe is inherently probabilistic.

### 4. The Concept of Duality and Complementarity
A major takeaway is the shift from "either/or" thinking to "both/and" thinking. 
* Through Einstein, we learned that light is both a wave and a particle. 
* Through Bohr, we learned the **Principle of Complementarity**: that an object can possess contradictory properties, and the way we choose to look at it determines which property we see.

### 5. Progress Through Conflict
Perhaps the most important takeaway is that scientific progress is often driven by intense disagreement. The intellectual rivalry between Einstein and Bohr did not stall physics; instead, it forced both men to sharpen their arguments, refine their theories, and push the boundaries of human understanding further than they ever could have alone."""
        ),
        ChatMessage(
            role="user",
            content="How did their research contribute to the efforts of the manhattan project?"
        ),
        ChatMessage(
            role="assistant",
            content="""While neither Einstein nor Bohr were "hands-on" researchers in the sense of building the actual bombs or managing the laboratory sites, their theoretical work provided the **essential scientific foundation** without which the Manhattan Project would have been impossible.

The Manhattan Project was essentially an attempt to turn the abstract, "spooky" theories of quantum mechanics into a massive, industrial-scale application of energy. Here is how their specific contributions paved the way:

### 1. Einstein: The Energy-Matter Connection
Einstein’s most direct contribution to the Manhattan Project was his most famous equation: **$E=mc^2$**.

*   **The Mechanism of Fission:** The entire project was based on the concept of nuclear fission—splitting an atom to release energy. Einstein’s equation provided the mathematical proof that a tiny amount of mass could be converted into a staggering amount of energy. 
*   **The "Why" of the Bomb:** Without $E=mc^2$, scientists would not have had the theoretical framework to calculate exactly how much energy would be released when a uranium or plutonium nucleus split. It explained the "payoff" of the reaction that the Manhattan Project was trying to trigger.

### 2. Bohr: The Architecture of the Nucleus
If Einstein provided the "how much" (the energy), Bohr provided the "where" and "how" (the structure).

*   **Understanding the Atom:** To manipulate an atom, you must first understand its structure. Bohr’s model of the atom and his work on electron shells were fundamental to understanding how atoms interact with one another and how they can be manipulated through bombardment.
*   **Isotopes and Neutron Capture:** The Manhattan Project relied heavily on the ability to manipulate specific isotopes (like Uranium-235). Bohr’s work on the quantum states of atoms allowed scientists to understand how neutrons interact with nuclei. This was critical for the "chain reaction"—the process where one splitting atom triggers another.
*   **The Role of the Observer and Measurement:** Bohr’s understanding of how particles behave when they are struck or measured was vital for the experimental physics required to refine uranium enrichment and plutonium production.

### 3. The "Human" Connection: Bohr’s Role in the Project
Beyond the math, Niels Bohr played a unique and highly influential role in the actual management and ethics of the project:

*   **Scientific Advisor:** Bohr was a key scientific consultant for the Manhattan Project. He traveled to the United States and worked closely with the project's leaders, including Robert Oppenheimer.
*   **The "Open World" Philosophy:** Bohr was deeply concerned about the political implications of the bomb. He famously advocated for "openness" in scientific research, fearing that if the secret of nuclear energy was kept only by a few nations, it would lead to a permanent state of global tension. He believed that the scientific community should share its findings to prevent a nuclear arms race—a debate that continues to this day.

### Summary Table

| Scientist | Theoretical Contribution | Application to Manhattan Project |
| :--- | :--- | :--- |
| **Einstein** | $E=mc^2$ (Mass-Energy Equivalence) | Provided the mathematical basis for the massive energy release in fission. |
| **Bohr** | Quantum Model of the Atom | Provided the understanding of atomic structure and how to manipulate nuclei. |
| **Bohr** | Scientific Consultation | Acted as a high-level advisor and helped shape the scientific direction of the project. |"""
        )
    ]
)


print(test_chat.context_string)


test_chat.generate_followup(
    max_retries=3,
    model_id="gemma-4-26B-A4B-it-Q4_K_M.gguf",
    append_to_chat=True
)

print(test_chat.context_string)