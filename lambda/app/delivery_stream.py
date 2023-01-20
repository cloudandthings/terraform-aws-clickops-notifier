import boto3


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


class FakeClient:
    def put_record_batch(DeliveryStreamName=None, Records=None):
        print(f"Delivering {len(Records)} to {DeliveryStreamName}")


class DeliveryStream:

    delivery_stream_name = None
    client = None

    def __init__(self, delivery_stream_name, *args, fake=False, **kwargs):
        self.delivery_stream_name = delivery_stream_name

        if not fake:
            self.client = boto3.client("firehose")
        else:
            self.client = FakeClient()

    event_buffer = []

    def _flush(self):
        if len(self.event_buffer) == 0:
            return

        for events in chunker(self.event_buffer, 500):
            records = [{"Data": bytes(event, "UTF-8") for event in events}]
            # TODO
            self.client.put_record_batch(
                DeliveryStreamName=self.delivery_stream_name, Records=records
            )

    def send(self, event):
        self.event_buffer.append(event)
        if len(self.event_buffer) >= 500:
            self._flush()
        pass

    def __del__(self):
        self._flush()
