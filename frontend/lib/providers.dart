import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api.dart';
import 'models.dart';

final gyaanApiProvider = Provider((_) => GyaanApi());

final dailyInsightsProvider = FutureProvider<List<ArticleSummary>>((ref) async {
  final api = ref.watch(gyaanApiProvider);
  return api.fetchDailyInsights();
});

final learnExplanationProvider = FutureProvider.family<ExplainResponse, Map<String, String>>((ref, params) async {
  final api = ref.watch(gyaanApiProvider);
  return api.explainTopic(params['query']!, params['depth']!);
});

final articleDetailProvider = FutureProvider.family<ArticleDetail, String>((ref, id) async {
  final api = ref.watch(gyaanApiProvider);
  return api.fetchArticleDetail(id);
});

final startupPipelineProvider = FutureProvider<int>((ref) async {
  final api = ref.watch(gyaanApiProvider);
  return api.scrapeArticles();
});
