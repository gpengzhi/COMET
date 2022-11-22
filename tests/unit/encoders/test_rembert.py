# -*- coding: utf-8 -*-
import unittest

from comet.encoders.rembert import RemBERTEncoder


class TestRemBERTEncoder(unittest.TestCase):

    bert = RemBERTEncoder.from_pretrained("google/rembert")

    def test_num_layers(self):
        self.assertEqual(self.bert.num_layers, 33)

    def test_output_units(self):
        self.assertEqual(self.bert.output_units, 1152)

    def test_max_positions(self):
        self.assertEqual(self.bert.max_positions, 510)

    def test_prepare_sample(self):
        sample = ["hello world, welcome to COMET!", "This is a batch"]
        model_input = self.bert.prepare_sample(sample)
        self.assertIn("input_ids", model_input)
        self.assertIn("attention_mask", model_input)
    
    def test_forward(self):
        sample = ["hello world, welcome to COMET!", "This is a batch"]
        model_input = self.bert.prepare_sample(sample)
        model_output = self.bert(**model_input)
        self.assertIn("wordemb", model_output)
        self.assertIn("sentemb", model_output)
        self.assertIn("all_layers", model_output)
        self.assertIn("attention_mask", model_output)
    
    def test_subword_tokenize(self):
        samples = ['the olympiacos revived <EOS>', "This is COMET ! <EOS>"]
        subwords, subword_mask, subword_lengths = self.bert.subword_tokenize(samples, pad=True)
        expected_tokenization = [
            ['[CLS]', '▁the', '▁olympia', 'cos', '▁reviv', 'ed', '▁<', 'E', 'OS', '>', '[SEP]'],
            ['[CLS]', '▁This', '▁is', '▁COME', 'T', '▁!', '▁<', 'E', 'OS', '>', '[SEP]']
        ]
        expected_mask = [
            [0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0]
        ]
        expected_lengths = [11, 11]
        self.assertListEqual(subwords, expected_tokenization)
        self.assertListEqual(subword_mask.int().tolist(), expected_mask)
        self.assertListEqual(subword_lengths, expected_lengths)
    
    def test_mask_start_tokens(self):
        tokenized_sentence = [
            ['[CLS]', '▁After', '▁the', '▁Greek', '▁war', '▁of', '▁in', 'dependence', '▁from', '▁the', '▁o', 'ttoman', '[SEP]'],
            ['[CLS]', '▁she', '▁was', '▁given', '▁the', '▁uk', '▁s', 'qui', 'r', 'rel', '[SEP]'],
        ]
        expected_mask = [
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        ]
        seq_len = [13, 11]
        mask = self.bert.mask_start_tokens(tokenized_sentence, seq_len)
        self.assertListEqual(mask.int().tolist(), expected_mask)

    def test_concat_sequences(self):
        source = ["Bem vindos ao COMET", "Isto é um exemplo!"]
        translations = ["Welcome to COMET!", "This is an example!"]
        source_input = self.bert.prepare_sample(source)
        translations_input = self.bert.prepare_sample(translations)
        expected_tokens = [
            [   312,  58230,  16833,    759,   1425, 148577,    862,    313,  26548,    596, 148577,    862,    646,    313],
            [   312,  58378,    921,    835,  17293,    646,    313,   1357,    619,    666,   7469,    646,    313,      0],
        ]
        seq_size = [14, 13]
        continuous_input = self.bert.concat_sequences([source_input, translations_input])
        self.assertListEqual(continuous_input[0]["input_ids"].tolist(), expected_tokens)
        self.assertListEqual(continuous_input[1].tolist(), seq_size)
