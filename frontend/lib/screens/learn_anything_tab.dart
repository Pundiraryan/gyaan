import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers.dart';

class LearnAnythingTab extends ConsumerStatefulWidget {
  const LearnAnythingTab({super.key});

  @override
  ConsumerState<LearnAnythingTab> createState() => _LearnAnythingTabState();
}

class _LearnAnythingTabState extends ConsumerState<LearnAnythingTab> {
  final _queryController = TextEditingController();
  String _selectedDepth = 'student';
  bool _submitted = false;
  bool _isSubmitting = false;
  double _progress = 0.0;
  Timer? _progressTimer;

  @override
  void dispose() {
    _progressTimer?.cancel();
    _queryController.dispose();
    super.dispose();
  }

  void _startProgress() {
    _progressTimer?.cancel();
    setState(() {
      _submitted = true;
      _isSubmitting = true;
      _progress = 0.12;
    });
    _progressTimer = Timer.periodic(const Duration(milliseconds: 450), (timer) {
      if (!mounted) {
        timer.cancel();
        return;
      }
      setState(() {
        _progress = (_progress < 0.9) ? _progress + 0.12 : 0.9;
      });
    });
  }

  void _stopProgress() {
    _progressTimer?.cancel();
    _progressTimer = null;
    if (!mounted) return;
    setState(() {
      _isSubmitting = false;
      _progress = 1.0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: _queryController,
            decoration: const InputDecoration(
              labelText: 'Learn anything...',
              border: OutlineInputBorder(),
              hintText: 'Explain Transformers',
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: _selectedDepth,
                  items: const [
                    DropdownMenuItem(value: 'beginner', child: Text('Beginner')),
                    DropdownMenuItem(value: 'student', child: Text('Student')),
                    DropdownMenuItem(value: 'engineer', child: Text('Engineer')),
                    DropdownMenuItem(value: 'expert', child: Text('Expert')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _selectedDepth = value);
                    }
                  },
                  decoration: const InputDecoration(labelText: 'Depth'),
                ),
              ),
              const SizedBox(width: 12),
              ElevatedButton(
                onPressed: () {
                  final query = _queryController.text.trim();
                  if (query.isEmpty) return;
                  _startProgress();
                },
                child: const Text('Explain'),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (_submitted)
            Expanded(
              child: Consumer(
                builder: (context, ref, _) {
                  final explanationAsync = ref.watch(
                    learnExplanationProvider({
                      'query': _queryController.text.trim(),
                      'depth': _selectedDepth,
                    }),
                  );
                  return explanationAsync.when(
                    data: (explanation) {
                      _stopProgress();
                      return SingleChildScrollView(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Explanation', style: Theme.of(context).textTheme.titleLarge),
                            const SizedBox(height: 12),
                            Text(explanation.explanation, style: Theme.of(context).textTheme.bodyLarge?.copyWith(height: 1.6)),
                            const SizedBox(height: 16),
                            Text('Key Concepts', style: Theme.of(context).textTheme.titleMedium),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 8,
                              runSpacing: 8,
                              children: explanation.keyConcepts.map((concept) => Chip(label: Text(concept))).toList(),
                            ),
                            const SizedBox(height: 16),
                            Text('Suggested Follow-ups', style: Theme.of(context).textTheme.titleMedium),
                            const SizedBox(height: 8),
                            ...explanation.suggestedFollowups.map((item) => ListTile(title: Text(item))),
                          ],
                        ),
                      );
                    },
                    loading: () => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        LinearProgressIndicator(value: _progress),
                        const SizedBox(height: 12),
                        Text(
                          _isSubmitting ? 'Generating a polished explanation...' : 'Preparing your request...',
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      ],
                    ),
                    error: (error, stack) {
                      _stopProgress();
                      return Center(child: Text('Unable to explain topic: $error'));
                    },
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
}
