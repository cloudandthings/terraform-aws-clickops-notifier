import boto3
import json
import logging


class FakeClient:
    def put_record_batch(self, **kwargs):
        num_records = len(kwargs.get("Records", []))
        logging.debug(f"FakeClient put_record_batch: {num_records} records")
        return {"FailedPutCount": 0}


class DeliveryStream:
    delivery_stream_name = None
    client = None

    def __init__(self, delivery_stream_name):
        self.delivery_stream_name = delivery_stream_name

        if self.delivery_stream_name is None:
            self.client = FakeClient()
        else:
            self.client = boto3.client("firehose")

    event_buffer = []

    def _flush(self) -> bool:
        if len(self.event_buffer) == 0:
            return True

        # print (f'put_record_batch: {len(self.event_buffer)} events in buffer.')
        success = True
        for pos in range(0, len(self.event_buffer), 500):
            # print (f'put_record_batch: Sending {len(events)} events.')
            records = []
            for event in self.event_buffer[pos : pos + 500]:
                records.append({"Data": bytes(json.dumps(event), "UTF-8")})
            response = self.client.put_record_batch(
                DeliveryStreamName=self.delivery_stream_name, Records=records
            )
            # Check response
            failed_put_count = response["FailedPutCount"]
            if failed_put_count > 0:
                # print(f'response={response}')
                success = False
        self.event_buffer = []
        return success

    def send(self, event) -> bool:
        self.event_buffer.append(event)
        # print (f'send: {len(self.event_buffer)} events in buffer.')
        if len(self.event_buffer) >= 500:
            return self._flush()
        return True

    def __del__(self):
        success = self._flush()
        if not success:
            raise Exception(
                "A problem occurred when delivering data, please review the error logs."
            )
