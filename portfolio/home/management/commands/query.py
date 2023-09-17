import os
from django.core.management.base import BaseCommand, CommandError
from home.agent import Agent


class Command(BaseCommand):

    help = "Query using Langchain by asking questions."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent = Agent()

    def add_arguments(self, parser):
        parser.add_argument("--query", default="", type=str, help="Ask me a question.")

    def handle(self, *args, **options):
        assert options["query"] != "", "Please provide a query."
        qa = self.agent.get_qa_chain()
        print(qa.run(options["query"]))