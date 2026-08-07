import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'models.dart';

class GyaanApi {
  static String get _baseUrl {
    const envUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
    if (envUrl.isNotEmpty) {
      return envUrl;
    }

    if (kIsWeb) {
      return 'http://localhost:8000/api';
    }

    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000/api';
    }

    return 'http://127.0.0.1:8000/api';
  }

  Future<List<ArticleSummary>> fetchDailyInsights() async {
    final response = await http.get(Uri.parse('$_baseUrl/daily-insights'));
    if (response.statusCode != 200) {
      throw Exception('Failed to load daily insights');
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    final insights = body['insights'] as List<dynamic>;
    return insights.map((item) => ArticleSummary.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<ArticleDetail> fetchArticleDetail(String id) async {
    final response = await http.get(Uri.parse('$_baseUrl/article/$id'));
    if (response.statusCode != 200) {
      throw Exception('Article not found');
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return ArticleDetail.fromJson(body);
  }

  Future<ExplainResponse> explainTopic(String query, String depth) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/explain'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'query': query,
        'depth': depth,
      }),
    );
    if (response.statusCode != 200) {
      throw Exception('Failed to generate explanation');
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return ExplainResponse.fromJson(body);
  }

  Future<int> scrapeArticles() async {
    final response = await http.post(Uri.parse('$_baseUrl/scrape'));
    if (response.statusCode != 200) {
      throw Exception('Failed to scrape latest articles');
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return body['scraped_articles'] as int;
  }
}
