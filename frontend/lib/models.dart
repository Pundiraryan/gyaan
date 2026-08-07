class ArticleSummary {
  final String id;
  final String title;
  final String snippet;
  final String source;
  final String? publishedAt;
  final double importanceScore;

  ArticleSummary({
    required this.id,
    required this.title,
    required this.snippet,
    required this.source,
    required this.publishedAt,
    required this.importanceScore,
  });

  factory ArticleSummary.fromJson(Map<String, dynamic> json) {
    return ArticleSummary(
      id: json['id'] as String,
      title: json['title'] as String,
      snippet: json['snippet'] as String,
      source: json['source'] as String,
      publishedAt: json['published_at'] as String?,
      importanceScore: (json['importance_score'] as num).toDouble(),
    );
  }
}

class ArticleDetail {
  final String id;
  final String title;
  final String source;
  final String url;
  final String? publishedAt;
  final String summary;
  final String plainEnglish;
  final String content;
  final List<String> concepts;
  final String whatHappened;
  final String whyItMatters;
  final String historicalContext;
  final String careerRelevance;
  final List<String> expertPerspectives;
  final String contrarianPerspective;
  final List<String> futurePredictions;
  final List<String> knowledgeGraph;

  ArticleDetail({
    required this.id,
    required this.title,
    required this.source,
    required this.url,
    required this.publishedAt,
    required this.summary,
    required this.plainEnglish,
    required this.content,
    required this.concepts,
    required this.whatHappened,
    required this.whyItMatters,
    required this.historicalContext,
    required this.careerRelevance,
    required this.expertPerspectives,
    required this.contrarianPerspective,
    required this.futurePredictions,
    required this.knowledgeGraph,
  });

  factory ArticleDetail.fromJson(Map<String, dynamic> json) {
    return ArticleDetail(
      id: json['id'] as String,
      title: json['title'] as String,
      source: json['source'] as String,
      url: json['url'] as String,
      publishedAt: json['published_at'] as String?,
      summary: json['summary'] as String,
      plainEnglish: json['plain_english'] as String,
      content: json['content'] as String,
      concepts: List<String>.from(json['concepts'] as List<dynamic>),
      whatHappened: json['what_happened'] as String,
      whyItMatters: json['why_it_matters'] as String,
      historicalContext: json['historical_context'] as String,
      careerRelevance: json['career_relevance'] as String,
      expertPerspectives: List<String>.from(json['expert_perspectives'] as List<dynamic>),
      contrarianPerspective: json['contrarian_perspective'] as String,
      futurePredictions: List<String>.from(json['future_predictions'] as List<dynamic>),
      knowledgeGraph: List<String>.from(json['knowledge_graph'] as List<dynamic>),
    );
  }
}

class ExplainResponse {
  final String query;
  final String depth;
  final String explanation;
  final List<String> keyConcepts;
  final List<String> suggestedFollowups;

  ExplainResponse({
    required this.query,
    required this.depth,
    required this.explanation,
    required this.keyConcepts,
    required this.suggestedFollowups,
  });

  factory ExplainResponse.fromJson(Map<String, dynamic> json) {
    return ExplainResponse(
      query: json['query'] as String,
      depth: json['depth'] as String,
      explanation: json['explanation'] as String,
      keyConcepts: List<String>.from(json['key_concepts'] as List<dynamic>),
      suggestedFollowups: List<String>.from(json['suggested_followups'] as List<dynamic>),
    );
  }
}
