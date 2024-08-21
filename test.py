from Drafter import Drafter
from Orienter import Orienter
from Sketcher import Sketcher
from extract import extract_thoughts, extract_proof
import logging
import time
import os
import json
from langchain.schema import AIMessage, HumanMessage, SystemMessage

def initialise_logger(name=None):
    logger = logging.getLogger(name=name)
    logger.setLevel(logging.INFO)
    start_time = time.strftime("%Y%m%d_%H%M%S")
    if name is not None:
        os.makedirs(f"logs/{name}/", exist_ok=True)
        handler = logging.FileHandler(f"logs/{name}/{start_time}.log")
    else:
        os.makedirs(f"logs/{start_time}_logs", exist_ok=True)
        handler = logging.FileHandler(f"logs/{start_time}_logs/{start_time}.log")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def thoughts_queue(informal_statement, informal_proof, formal_statement):
    orienter = Orienter(model="gpt-3.5-turbo")

    prompt_logger = initialise_logger("prompt")
    sketcher_logger = initialise_logger("sketcher")

    drafter = Drafter(
        prompt_template_path="path/to/prompt_template", model="gpt-3.5-turbo"
    )

    sketcher = Sketcher(
        example_path="data/paper_prompt_examples",
        directory="sin_gt_zero",
        logger=prompt_logger,
    )

    thoughts_to_process = [(informal_statement, informal_proof, formal_statement, True)]
    initial_problem = (informal_statement, informal_proof, formal_statement)

    while thoughts_to_process:
        (
            current_informal_statement,
            current_informal_proof,
            current_formal_statement,
            is_initial_problem,
        ) = thoughts_to_process.pop(0)
        response = orienter.orient(
            current_informal_statement,
            current_informal_proof,
            current_formal_statement,
            temperature=0,
        )

        sketcher_logger.info(
            "current_informal_statement:\n" + current_informal_statement
        )

        sketcher_logger.info(response)

        print("##### RESPONSE #####")
        print(response)

        thoughts = extract_thoughts(response)
        print("##### LEMMAS #####")
        for i, thought in enumerate(thoughts):
            print(thought)
            sketcher_logger.info(thought)
            thought_informal_statement = thought.get("thought")
            thought_formal_statement = thought.get("code")
            thought_informal_proof = drafter.write_proof_openai(
                informal_statement=thought_informal_statement,
                formal_statement=thought_formal_statement,
            )
            thoughts_to_process.append(
                (
                    thought_informal_statement,
                    thought_informal_proof,
                    thought_formal_statement,
                    False,
                )
            )
            print(thought_informal_statement)
            print(thought_formal_statement)

        proof = extract_proof(response)
        print("##### PROOF #####")
        print(proof)

        if not is_initial_problem:
            informal_proof = drafter.write_proof_openai(
                informal_statement=current_informal_statement,
                formal_statement=current_formal_statement,
            )

            sketcher_logger.info(f"\n Informal proof for thought {i}:\n")
            sketcher_logger.info(informal_proof)
            print(informal_proof)
            print("\n\n")

            sketch = sketcher.create_formal_sketch(
                informal_statement=current_informal_statement,
                informal_proof=informal_proof,
                formal_statement=current_formal_statement,
            )
            print("##### SKETCH #####")

            sketcher_logger.info("\n##### SKETCH #####\n")
            sketcher_logger.info("\n" + current_formal_statement + "\n" + sketch)
            print(current_formal_statement)
            print(sketch)
            print("\n\n")

    initial_informal_statement, initial_informal_proof, initial_formal_statement = (
        initial_problem
    )
    sketch = sketcher.create_formal_sketch(
        informal_statement=initial_informal_statement,
        informal_proof=initial_informal_proof,
        formal_statement=initial_formal_statement,
    )
    print("##### SKETCH #####")
    sketcher_logger.info("\n##### SKETCH #####\n")
    sketcher_logger.info("\n" + initial_formal_statement + "\n" + sketch)
    print(initial_formal_statement)
    print(sketch)
    print("\n\n")


def dict_to_message(self, message_dict):
    if message_dict["role"] == "system":
        return SystemMessage(message_dict["content"])
    elif message_dict["role"] == "human":
        return HumanMessage(message_dict["content"])
    elif message_dict["role"] == "ai":
        return AIMessage(message_dict["content"])
    else:
        raise ValueError("Invalid message role")

def extract_and_query(directory: str):
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            with open(os.path.join(directory, file), "r") as f:
                messages_as_dicts = json.load(f)
            messages = [dict_to_message(msg) for msg in messages_as_dicts]
            response = response = llm.query(langchain_msgs=messages, temperature=0.0, max_tokens=4000)


if __name__ == "__main__":
    informal_statement = "Find the minimum value of $\frac{9x^2\sin^2 x + 4}{x\sin x}$ for $0 < x < \pi$. Show that it is 12."
    informal_proof = "Let $y = x \sin x$. It suffices to show that $12 \leq \frac{9y^2 + 4}{y}. It is trivial to see that $y > 0$. Then one can multiply both sides by $y$ and it suffices to show $12y \leq 9y^2 + 4$. This can be done by the sum of squares method."
    formal_statement = """theorem
  fixes x::real
  assumes "0<x" "x<pi"
  shows "12 \<le> ((9 * (x^2 * (sin x)^2)) + 4) / (x * sin x)\""""

    orienter = Orienter(model="gpt-3.5-turbo")

    thoughts_queue(informal_statement, informal_proof, formal_statement)

    # response = orienter.orient(informal_statement, informal_proof, formal_statement, temperature=0)

    # print("##### RESPONSE #####")
    # print(response)

    # thoughts = extract_thoughts(response)
    # print("##### THOUGHTS #####")
    # for thought in thoughts:
    #     print(thought)
    #     print(thought.get('thought'))
    #     print(thought.get('code'))

    # proof = extract_proof(response)
    # print("##### PROOF #####")
    # print(proof)

    # Drafter = Drafter(
    #     prompt_template_path="path/to/prompt_template",
    #     model="gpt-3.5-turbo"
    # )

    # for thought in thoughts:
    #     informal_statement = thought.get('thought')
    #     formal_statement = thought.get('code')

    #     informal_proof = Drafter.write_proof_openai(informal_statement=informal_statement, formal_statement=formal_statement)
    #     print(informal_proof)
    #     print("\n\n")
