import logging
import re
from typing import Dict, List, Any, Optional
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.sentiment import SentimentIntensityAnalyzer
import string

logger = logging.getLogger(__name__)

class TextAnalyzer:
    """Text analysis module to extract writing style, tone, and patterns"""
    
    def __init__(self):
        # Download required NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK data: {e}")
        
        self.stop_words = set(stopwords.words('english'))
        self.sia = SentimentIntensityAnalyzer()
    
    def analyze_writing_style(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze writing style from multiple texts"""
        if not texts:
            return {}
        
        # Combine all texts
        combined_text = ' '.join(texts)
        
        # Basic statistics
        stats = self._get_basic_stats(combined_text)
        
        # Vocabulary analysis
        vocabulary = self._analyze_vocabulary(combined_text)
        
        # Sentence analysis
        sentences = self._analyze_sentences(combined_text)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(combined_text)
        
        # Writing patterns
        patterns = self._analyze_patterns(combined_text)
        
        # Common phrases and expressions
        phrases = self._extract_common_phrases(combined_text)
        
        return {
            'basic_stats': stats,
            'vocabulary': vocabulary,
            'sentences': sentences,
            'sentiment': sentiment,
            'patterns': patterns,
            'common_phrases': phrases,
            'sample_texts': texts[:5]  # Include sample texts for reference
        }
    
    def _get_basic_stats(self, text: str) -> Dict[str, Any]:
        """Get basic text statistics"""
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        
        # Remove punctuation
        words = [word for word in words if word.isalpha()]
        
        return {
            'total_words': len(words),
            'total_sentences': len(sentences),
            'total_characters': len(text),
            'average_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'average_characters_per_word': sum(len(word) for word in words) / len(words) if words else 0,
            'unique_words': len(set(words)),
            'vocabulary_richness': len(set(words)) / len(words) if words else 0
        }
    
    def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary characteristics"""
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha()]
        
        # Word frequency
        word_freq = Counter(words)
        most_common = word_freq.most_common(20)
        
        # Word length analysis
        word_lengths = [len(word) for word in words]
        
        # POS tagging
        pos_tags = pos_tag(words)
        pos_counts = Counter(tag for word, tag in pos_tags)
        
        # Remove stopwords for analysis
        content_words = [word for word in words if word not in self.stop_words]
        content_word_freq = Counter(content_words)
        
        return {
            'most_common_words': most_common,
            'most_common_content_words': content_word_freq.most_common(15),
            'average_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            'longest_words': sorted(set(words), key=len, reverse=True)[:10],
            'pos_distribution': dict(pos_counts),
            'stopword_ratio': len([w for w in words if w in self.stop_words]) / len(words) if words else 0
        }
    
    def _analyze_sentences(self, text: str) -> Dict[str, Any]:
        """Analyze sentence structure"""
        sentences = sent_tokenize(text)
        
        sentence_lengths = [len(word_tokenize(sent)) for sent in sentences]
        
        # Sentence complexity (average clauses per sentence)
        complex_sentences = len([s for s in sentences if ',' in s or ';' in s or ':' in s])
        
        # Question vs statement ratio
        questions = len([s for s in sentences if s.strip().endswith('?')])
        exclamations = len([s for s in sentences if s.strip().endswith('!')])
        
        return {
            'total_sentences': len(sentences),
            'average_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'shortest_sentence': min(sentence_lengths) if sentence_lengths else 0,
            'longest_sentence': max(sentence_lengths) if sentence_lengths else 0,
            'complexity_ratio': complex_sentences / len(sentences) if sentences else 0,
            'question_ratio': questions / len(sentences) if sentences else 0,
            'exclamation_ratio': exclamations / len(sentences) if sentences else 0
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment patterns"""
        sentences = sent_tokenize(text)
        
        sentiments = []
        for sentence in sentences:
            sentiment_scores = self.sia.polarity_scores(sentence)
            sentiments.append(sentiment_scores)
        
        # Average sentiment scores
        avg_scores = {
            'positive': sum(s['pos'] for s in sentiments) / len(sentiments) if sentiments else 0,
            'negative': sum(s['neg'] for s in sentiments) / len(sentiments) if sentiments else 0,
            'neutral': sum(s['neu'] for s in sentiments) / len(sentiments) if sentiments else 0,
            'compound': sum(s['compound'] for s in sentiments) / len(sentiments) if sentiments else 0
        }
        
        # Overall sentiment classification
        if avg_scores['compound'] >= 0.05:
            overall_sentiment = 'positive'
        elif avg_scores['compound'] <= -0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        return {
            'overall_sentiment': overall_sentiment,
            'average_scores': avg_scores,
            'sentiment_distribution': {
                'positive_sentences': len([s for s in sentiments if s['compound'] > 0.05]),
                'negative_sentences': len([s for s in sentiments if s['compound'] < -0.05]),
                'neutral_sentences': len([s for s in sentiments if -0.05 <= s['compound'] <= 0.05])
            }
        }
    
    def _analyze_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze writing patterns and style markers"""
        patterns = {}
        
        # Use of contractions
        contractions = re.findall(r"\b\w+'\w+\b", text)
        patterns['contraction_usage'] = len(contractions)
        
        # Use of numbers
        numbers = re.findall(r'\b\d+\b', text)
        patterns['number_usage'] = len(numbers)
        
        # Use of punctuation
        punctuation_counts = {
            'commas': text.count(','),
            'semicolons': text.count(';'),
            'colons': text.count(':'),
            'dashes': text.count('—') + text.count('-'),
            'parentheses': text.count('(') + text.count(')'),
            'quotes': text.count('"') + text.count("'")
        }
        patterns['punctuation'] = punctuation_counts
        
        # Use of capitalization
        caps_words = re.findall(r'\b[A-Z][A-Z]+\b', text)
        patterns['all_caps_usage'] = len(caps_words)
        
        # Use of italics/emphasis markers
        emphasis_markers = text.count('*') + text.count('_')
        patterns['emphasis_usage'] = emphasis_markers
        
        # Paragraph breaks
        paragraphs = text.split('\n\n')
        patterns['paragraph_count'] = len([p for p in paragraphs if p.strip()])
        
        return patterns
    
    def _extract_common_phrases(self, text: str) -> Dict[str, Any]:
        """Extract common phrases and expressions"""
        # Extract 2-gram and 3-gram phrases
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalpha()]
        
        # 2-grams
        bigrams = []
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            bigrams.append(bigram)
        
        bigram_freq = Counter(bigrams)
        
        # 3-grams
        trigrams = []
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            trigrams.append(trigram)
        
        trigram_freq = Counter(trigrams)
        
        # Extract quotes
        quotes = re.findall(r'"([^"]+)"', text)
        
        # Extract questions
        questions = re.findall(r'[^.!?]*\?', text)
        
        return {
            'common_bigrams': bigram_freq.most_common(10),
            'common_trigrams': trigram_freq.most_common(10),
            'quotes': quotes[:5],
            'questions': questions[:5]
        }
    
    def extract_personality_traits(self, texts: List[str]) -> Dict[str, Any]:
        """Extract personality traits from writing style"""
        style_analysis = self.analyze_writing_style(texts)
        
        traits = {}
        
        # Communication style
        avg_sentence_length = style_analysis['sentences']['average_sentence_length']
        if avg_sentence_length > 20:
            traits['communication_style'] = 'detailed_and_comprehensive'
        elif avg_sentence_length > 15:
            traits['communication_style'] = 'moderately_detailed'
        else:
            traits['communication_style'] = 'concise_and_direct'
        
        # Formality level
        contraction_usage = style_analysis['patterns']['contraction_usage']
        if contraction_usage > 10:
            traits['formality'] = 'casual_and_conversational'
        elif contraction_usage > 5:
            traits['formality'] = 'moderately_formal'
        else:
            traits['formality'] = 'formal_and_professional'
        
        # Emotional tone
        sentiment = style_analysis['sentiment']['overall_sentiment']
        traits['emotional_tone'] = sentiment
        
        # Confidence level
        exclamation_ratio = style_analysis['sentences']['exclamation_ratio']
        if exclamation_ratio > 0.1:
            traits['confidence'] = 'highly_enthusiastic'
        elif exclamation_ratio > 0.05:
            traits['confidence'] = 'moderately_confident'
        else:
            traits['confidence'] = 'measured_and_cautious'
        
        # Questioning style
        question_ratio = style_analysis['sentences']['question_ratio']
        if question_ratio > 0.2:
            traits['questioning_style'] = 'inquisitive_and_curious'
        elif question_ratio > 0.1:
            traits['questioning_style'] = 'moderately_inquisitive'
        else:
            traits['questioning_style'] = 'declarative_and_assertive'
        
        return traits




