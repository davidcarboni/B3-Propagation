import unittest
import re
import b3
from b3 import b3_trace_id, b3_parent_span_id, b3_span_id, b3_sampled, b3_flags


class TestB3(unittest.TestCase):

    def tearDown(self):
        b3.debug = False
        b3._end_subspan()

    def test_should_generate_root_span_ids(self):
        # Given
        # No B3 headers - this is the root span
        b3.start_span({})

        # When
        # We get the B3 values
        values = b3.values()

        # Then
        # Both trace ID and span ID should have been genenated
        self.assertTrue(values[b3_trace_id])
        self.assertTrue(values[b3_span_id])
        # The IDs should be 16 characters of hex
        self.assertTrue(re.match("[a-fA-F0-9]{16}", values[b3_trace_id]))
        self.assertTrue(re.match("[a-fA-F0-9]{16}", values[b3_span_id]))

    def test_should_maintain_trace_id(self):
        # Given
        # A trace ID in the B3 headers
        trace_id = "Barbapapa"
        b3.start_span({b3_trace_id: trace_id})

        # When
        # We get b3 values and update onward request headers
        values = b3.values()
        headers = b3._start_subspan()

        # Then
        # The incoming trace ID should be maintained
        self.assertEqual(trace_id, values[b3_trace_id])
        self.assertEqual(trace_id, headers[b3_trace_id])

    def test_should_propagate_span_id_as_parent(self):
        # Given
        # A trace ID in the B3 headers
        span_id = "Barbabright"
        b3.start_span({b3_span_id: span_id})

        # When
        # We update onward request headers
        headers = b3._start_subspan()

        # Then
        # The incoming trace ID should be propagated
        self.assertEqual(span_id, headers[b3_parent_span_id])

    def test_should_propagate_with_new_span_id(self):
        # Given
        # A trace ID in the B3 headers
        span_id = "Barbazoo"
        b3.start_span({b3_span_id: span_id})

        # When
        # We update onward request headers
        headers = b3._start_subspan()

        # Then
        # The incoming trace ID should be propagated
        self.assertNotEqual(span_id, headers[b3_span_id])
        # The ID should be 16 characters of hex
        self.assertTrue(re.match("[a-fA-F0-9]{16}", headers[b3_span_id]))

    def test_should_not_set_sampled(self):
        # Given
        # Sampled is not set in the request headers
        b3.start_span({})

        # When
        # We get b3 values and update onward request headers
        values = b3.values()
        headers = b3._start_subspan()

        # Then
        # Sampled should not be set and should
        # remain absent from onward request headers
        self.assertIsNone(values[b3_sampled])
        self.assertFalse(b3_sampled in headers)

    def test_should_maintain_sampled(self):
        # Given
        # Sampled is not set in the request headers
        sampled = '0'
        b3.start_span({b3_sampled: sampled})

        # When
        # We get b3 values and update onward request headers
        values = b3.values()
        headers = b3._start_subspan()

        # Then
        # The Sampled value should be maintained
        self.assertEqual(sampled, values[b3_sampled])
        self.assertEqual(sampled, headers[b3_sampled])

    def test_should_maintain_flags_for_debug(self):
        # Given
        # Flags is set in the B3 headers
        flags = '1'
        b3.start_span({b3_flags: flags})

        # When
        # We get b3 values and update onward request headers
        values = b3.values()
        headers = b3._start_subspan()

        # Then
        # Flags should be set to 1 to indicate debug
        self.assertEqual(flags, values[b3.b3_flags])
        self.assertEqual(flags, headers[b3_flags])

    def test_should_set_flags_for_debug(self):
        # Given
        # We have set debug on
        b3.debug = True
        b3.start_span({})

        # When
        # We get b3 values and update onward request headers
        values = b3.values()
        headers = b3._start_subspan()

        # Then
        # Flags should be set to 1 to indicate debug
        self.assertEqual("1", values[b3_flags])
        self.assertEqual("1", headers[b3_flags])

    def test_should_update_span_info_on_subspan_start(self):
        # Given
        # We have a full set of span values
        b3.start_span({b3_sampled: "1", b3_flags: "1"})

        # When
        # We start a subspan
        span = b3.values()
        b3._start_subspan()

        # Then
        # Values should now reflect the sub-span
        subspan = b3.values()
        self.assertEqual(span[b3_trace_id], subspan[b3_trace_id])
        self.assertEqual(span[b3_span_id], subspan[b3_parent_span_id])
        self.assertNotEqual(span[b3_span_id], subspan[b3_span_id])
        self.assertEqual(span[b3_sampled], subspan[b3_sampled])
        self.assertEqual(span[b3_flags], subspan[b3_flags])

    def test_should_revert_span_info_on_subspan_end(self):
        # Given
        # We have a full set of span values and a subspan
        b3.start_span({b3_sampled: "1", b3_flags: "1"})
        span = b3.values()
        b3._start_subspan()

        # When
        # We end the subspan
        b3._end_subspan()

        # Then
        # Values should now reflect the sub-span
        reverted = b3.values()
        self.assertEqual(span[b3_trace_id], reverted[b3_trace_id])
        self.assertEqual(span[b3_parent_span_id], reverted[b3_parent_span_id])
        self.assertEqual(span[b3_span_id], reverted[b3_span_id])
        self.assertEqual(span[b3_sampled], reverted[b3_sampled])
        self.assertEqual(span[b3_flags], reverted[b3_flags])

    def test_should_update_headers_if_passed(self):
        # Given
        # We have some existing headers
        headers_original = {'Barbabeau': 'Barbalala'}

        # When
        # We update the headers
        headers_updated = b3._start_subspan(headers_original)

        # Then
        # headers should still contain the original header values
        # https://stackoverflow.com/questions/9323749/python-check-if-one-dictionary-is-a-subset-of-another-larger-dictionary
        self.assertTrue(set(headers_updated).issuperset(set(headers_original)))


if __name__ == '__main__':
    unittest.main()
