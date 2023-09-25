from django.core.management.base import BaseCommand
from home.agent import Agent


class Command(BaseCommand):

    help = "Query using Langchain agent by asking questions. You may set the number of times you want to type in and then chat."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = Agent(verbose=True)

    def add_arguments(self, parser):
        parser.add_argument("-n", "--number_of_messages", default=3, type=int, help="Number of messages to type in.")

    def handle(self, *args, **options):
        assert options["number_of_messages"] > 0, "`number_of_messages` or `n` must be greater than 0."
        qa_agent = self.agent.get_qa_agent_with_memory_chain()
        ctr = options["number_of_messages"]
        print("\n\n==================== Start of conversation ====================\n\n")
        try:
            while ctr > 0:
                try:
                    query = input("Ask me a question: ")
                    print(qa_agent.run((query)))
                    ctr -= 1
                    if ctr == 0:
                        print("\n\n==================== End of conversation ====================\n\n")
                except Exception as e:
                    print(e)
                    continue
        except KeyboardInterrupt:
            print("\n\n==================== Ending conversation ====================\n\n")
        except Exception as e:
            print("Main exception: ", e)