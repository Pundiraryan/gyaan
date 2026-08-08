import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers.dart';
import 'insight_detail_screen.dart';

class DailyInsightsTab extends ConsumerWidget {
  const DailyInsightsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final startupAsync = ref.watch(startupPipelineProvider);
    return startupAsync.when(
      data: (_) {
        final insightsAsync = ref.watch(dailyInsightsProvider);
        return insightsAsync.when(
          data: (insights) {
            if (insights.isEmpty) {
              return const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text('No insights are available yet. Please refresh the feed.'),
                ),
              );
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: insights.length,
              itemBuilder: (context, index) {
                final insight = insights[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Card(
                    clipBehavior: Clip.antiAlias,
                    child: InkWell(
                      onTap: () {
                        Navigator.of(context).push(MaterialPageRoute(
                          builder: (_) => InsightDetailScreen(articleId: insight.id),
                        ));
                      },
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                              Theme.of(context).colorScheme.surface.withValues(alpha: 0.9),
                            ],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              insight.title,
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Text(
                              insight.snippet,
                              maxLines: 4,
                              overflow: TextOverflow.ellipsis,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.5),
                            ),
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    'Priority ${insight.importanceScore.toStringAsFixed(2)}',
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                ),
                                FilledButton.tonal(
                                  onPressed: () {
                                    Navigator.of(context).push(MaterialPageRoute(
                                      builder: (_) => InsightDetailScreen(articleId: insight.id),
                                    ));
                                  },
                                  child: const Text('Explore More'),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => Center(child: Text('Unable to load insights: $error')),
        );
      },
      loading: () => const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Fetching latest articles and running the pipeline...'),
          ],
        ),
      ),
      error: (error, stack) => Center(child: Text('Failed to initialize content: $error')),
    );
  }
}
