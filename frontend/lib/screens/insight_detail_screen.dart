import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers.dart';

class InsightDetailScreen extends ConsumerWidget {
  final String articleId;

  const InsightDetailScreen({super.key, required this.articleId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final articleAsync = ref.watch(articleDetailProvider(articleId));
    return Scaffold(
      appBar: AppBar(title: const Text('Insight Detail')),
      body: articleAsync.when(
        data: (article) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeroCard(context, article),
                const SizedBox(height: 16),
                _buildSection(context, 'One Sentence Summary', article.summary),
                _buildSection(context, 'Plain English Translation', article.plainEnglish),
                _buildSection(context, 'What Happened?', article.whatHappened),
                _buildSection(context, 'Why Does This Matter?', article.whyItMatters),
                _buildSection(context, 'Key Concepts', null, concepts: article.concepts),
                _buildSection(context, 'Expert Perspectives', null, bullets: article.expertPerspectives),
                _buildSection(context, 'Contrarian Perspective', article.contrarianPerspective),
                _buildSection(context, 'Future Predictions', null, bullets: article.futurePredictions),
                _buildSection(context, 'Knowledge Graph', null, bullets: article.knowledgeGraph),
              ],
            ),
          );
        },
        loading: () => const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 12),
              Text('Preparing the article analysis...'),
            ],
          ),
        ),
        error: (error, stack) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.article_outlined, size: 48),
                const SizedBox(height: 12),
                Text(
                  'We could not load this article right now.',
                  style: Theme.of(context).textTheme.titleMedium,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                Text(
                  'Please try again in a moment.',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: () => ref.invalidate(articleDetailProvider(articleId)),
                  icon: const Icon(Icons.refresh),
                  label: const Text('Try again'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeroCard(BuildContext context, article) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(article.title, style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 8),
            Text(
              '${article.source} • ${article.publishedAt ?? 'Unknown'}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 10),
            Text(
              article.summary,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(
    BuildContext context,
    String title,
    String? body, {
    List<String>? bullets,
    List<String>? concepts,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 10),
            if (body != null && body.isNotEmpty)
              Text(body, style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6))
            else if (bullets != null && bullets.isNotEmpty)
              ...bullets.map((item) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text('• $item', style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.5)),
                  ))
            else if (concepts != null && concepts.isNotEmpty)
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: concepts.map((concept) => Chip(label: Text(concept))).toList(),
              )
            else
              Text('Details will appear here once the analysis is ready.', style: Theme.of(context).textTheme.bodyMedium),
          ],
        ),
      ),
    );
  }
}
