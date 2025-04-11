import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:provider/provider.dart';
import 'package:storypals_mobile/providers/child_provider.dart';
import 'package:storypals_mobile/widgets/insight_card.dart';
import 'package:storypals_mobile/widgets/progress_chart.dart';
import 'package:storypals_mobile/widgets/sleep_schedule.dart';
import 'package:storypals_mobile/widgets/word_of_day.dart';
import 'package:storypals_mobile/widgets/chat_history.dart';
import 'package:storypals_mobile/widgets/goal_setter.dart';
import 'package:storypals_mobile/theme/app_theme.dart';

class ParentDashboard extends StatefulWidget {
  final int childId;

  const ParentDashboard({Key? key, required this.childId}) : super(key: key);

  @override
  _ParentDashboardState createState() => _ParentDashboardState();
}

class _ParentDashboardState extends State<ParentDashboard> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeIn,
      ),
    );
    _animationController.forward();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<ChildProvider>(
      builder: (context, childProvider, _) {
        final child = childProvider.getChild(widget.childId);
        if (child == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return Scaffold(
          backgroundColor: AppTheme.background,
          body: FadeTransition(
            opacity: _fadeAnimation,
            child: CustomScrollView(
              slivers: [
                _buildAppBar(child),
                _buildStatsSection(child),
                _buildTabBar(),
                _buildTabView(child),
              ],
            ),
          ),
        );
      },
    );
  }

  SliverAppBar _buildAppBar(Child child) {
    return SliverAppBar(
      expandedHeight: 200.0,
      floating: false,
      pinned: true,
      backgroundColor: AppTheme.primary,
      flexibleSpace: FlexibleSpaceBar(
        title: Text(
          '${child.name}\'s Dashboard',
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                AppTheme.primary,
                AppTheme.primary.withOpacity(0.8),
              ],
            ),
          ),
          child: const Center(
            child: Icon(
              Icons.face,
              size: 80,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }

  SliverToBoxAdapter _buildStatsSection(Child child) {
    return SliverToBoxAdapter(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: InsightCard(
                    title: 'Vocabulary Progress',
                    value: '${child.vocabularyProgress}%',
                    icon: Icons.book,
                    color: AppTheme.accent,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: InsightCard(
                    title: 'Sleep Consistency',
                    value: '${child.sleepConsistency}%',
                    icon: Icons.bedtime,
                    color: AppTheme.secondary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: InsightCard(
                    title: 'Learning Goals',
                    value: '${child.completedGoals}/${child.totalGoals}',
                    icon: Icons.flag,
                    color: AppTheme.tertiary,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: InsightCard(
                    title: 'Chat Sessions',
                    value: child.totalSessions.toString(),
                    icon: Icons.chat,
                    color: AppTheme.primary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  SliverToBoxAdapter _buildTabBar() {
    return SliverToBoxAdapter(
      child: Container(
        color: AppTheme.background,
        child: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primary,
          labelColor: AppTheme.primary,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(text: 'Progress'),
            Tab(text: 'Goals'),
            Tab(text: 'History'),
          ],
        ),
      ),
    );
  }

  SliverFillRemaining _buildTabView(Child child) {
    return SliverFillRemaining(
      child: TabBarView(
        controller: _tabController,
        children: [
          _buildProgressTab(child),
          _buildGoalsTab(child),
          _buildHistoryTab(child),
        ],
      ),
    );
  }

  Widget _buildProgressTab(Child child) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Learning Progress',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ProgressChart(data: child.progressData),
          const SizedBox(height: 24),
          const Text(
            'Word of the Day',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          WordOfDayCard(word: child.wordOfDay),
          const SizedBox(height: 24),
          const Text(
            'Sleep Schedule',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          SleepScheduleCard(schedule: child.sleepSchedule),
        ],
      ),
    );
  }

  Widget _buildGoalsTab(Child child) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Set New Goals',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          GoalSetter(childId: child.id),
          const SizedBox(height: 24),
          const Text(
            'Active Goals',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ...child.activeGoals.map((goal) => GoalCard(goal: goal)),
        ],
      ),
    );
  }

  Widget _buildHistoryTab(Child child) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Recent Conversations',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ChatHistoryList(sessions: child.recentSessions),
          const SizedBox(height: 24),
          const Text(
            'Learning Insights',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          ...child.insights.map((insight) => InsightDetailCard(insight: insight)),
        ],
      ),
    );
  }
} 