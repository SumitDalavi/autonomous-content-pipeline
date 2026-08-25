import os
import json
from datetime import datetime

class ContentPipeline:
    def __init__(self, topic):
        self.topic = topic
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def fetch_data(self):
        """Simulate fetching data for the topic."""
        return [
            {"source": "mock_api_1", "content": f"Information about {self.topic}"},
            {"source": "mock_api_2", "content": f"More details on {self.topic}"}
        ]

    def generate_content(self, data):
        """Simulate LLM generating content based on fetched data."""
        # In a real app, this would call OpenAI/Anthropic API
        content = f"# Generated Article: {self.topic.title()}\n\n"
        for item in data:
            content += f"- Derived from {item['source']}: {item['content']}\n"
        content += "\nConclusion: AI content generation is efficient."
        return content

    def save_output(self, content):
        """Save the generated content to a markdown file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.topic.replace(' ', '_')}_{timestamp}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath

    def run(self):
        """Execute the full pipeline."""
        print(f"Starting pipeline for topic: {self.topic}")
        data = self.fetch_data()
        content = self.generate_content(data)
        filepath = self.save_output(content)
        print(f"Pipeline complete. Output saved to {filepath}")
        return filepath

if __name__ == "__main__":
    pipeline = ContentPipeline("AI advancements in 2026")
    pipeline.run()
