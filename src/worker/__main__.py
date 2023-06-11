import json

import click
import pika
from borb.pdf import Document, Paragraph, PDF, Page, SingleColumnLayout

from constants import pdfs_folder


def callback(channel, method, properties, body) -> None:  # type ignore
    json_f = json.loads(body)

    pdf = Document()
    page = Page()
    layout = SingleColumnLayout(page)
    layout.add(Paragraph(f"Username: {json_f['username']}"))
    layout.add(Paragraph(f"Sex: {json_f['sex']}"))
    layout.add(Paragraph(f"Session count: {json_f['session_count']}"))
    layout.add(Paragraph(f"Win: {json_f['win_count']}"))
    layout.add(Paragraph(f"Lose: {json_f['lose_count']}"))
    layout.add(Paragraph(f"Global time: {json_f['time']}"))
    pdf.append_page(page)

    with open(str(pdfs_folder / f"{json_f['username']}.pdf"), "wb") as f:
        PDF.dumps(f, pdf)

    channel.basic_ack(delivery_tag=method.delivery_tag)


@click.command()
@click.option("--host", default="localhost", type=str)
@click.option("--port", default=5672, type=int)
@click.option("--queue", default="rabbitmqqueue", type=str)
def main(host: str, port: int, queue: str) -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port)
    )
    print("Worker is connected", flush=True)
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    print("Worker starts consuming", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
