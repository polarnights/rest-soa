import pika
import sys
from fpdf import FPDF


connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='statistic_requests', durable=True)

def get_info(data, field, default_value, output_name):
    for tmp in data: 
        if ':' in tmp:
            l, r = tmp.split(':')
            if (l == field):
                return output_name + ': ' + r
    return output_name + ': ' + default_value

def callback(ch, method, properties, body):
    print('Callback', flush=True)
    link = body.decode()
    ch.basic_ack(delivery_tag=method.delivery_tag)
    data = link.split('#')
    num = str(data[-1])
    print(num, flush=True)
    pdf = FPDF('P', 'mm')
    pdf.set_font('Arial', '', 14)

    pdf.add_page()
    pdf.write(5, get_info(data, 'nickname', 'Not stated', 'nickname'))
    pdf.write(5, get_info(data, 'pp', 'Not stated', 'Profile picture'))
    pdf.write(5, get_info(data, 'gender', 'Not stated', 'gender'))
    pdf.write(5, get_info(data, 'email', 'Not stated', 'e-mail'))
    pdf.write(5, get_info(data, 'gamecnt', '0', 'Played games count'))
    pdf.write(5, get_info(data, 'winctn', '0', 'Won games count'))
    pdf.write(5, get_info(data, 'losscnt', '0', 'Lost games count'))
    pdf.write(5, get_info(data, 'time', '0', 'Total game time (seconds)'))
    pdf.output('/pdfs/' + num + '.pdf','F')

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='statistic_requests', on_message_callback=callback)

channel.start_consuming()