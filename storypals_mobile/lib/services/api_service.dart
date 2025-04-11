import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000';
  final SharedPreferences _prefs;

  ApiService(this._prefs);

  static Future<ApiService> create() async {
    final prefs = await SharedPreferences.getInstance();
    return ApiService(prefs);
  }

  Future<void> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      await _prefs.setString('email', email);
    } else {
      throw Exception('Login failed: ${response.body}');
    }
  }

  Future<void> register(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      await _prefs.setString('email', email);
    } else {
      throw Exception('Registration failed: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> createChild(
    String name,
    int age,
    Map<String, bool> preferences,
  ) async {
    final email = _prefs.getString('email');
    if (email == null) {
      throw Exception('Not logged in');
    }

    final response = await http.post(
      Uri.parse('$baseUrl/api/child/create'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': email,
      },
      body: jsonEncode({
        'name': name,
        'age': age,
        'interests': preferences.entries
            .where((entry) => entry.value)
            .map((entry) => entry.key)
            .toList(),
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to create child: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> sendMessage(String message, String childId) async {
    final email = _prefs.getString('email');
    if (email == null) throw Exception('Not logged in');

    final response = await http.post(
      Uri.parse('$baseUrl/chat'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': email,
      },
      body: jsonEncode({
        'message': message,
        'child_id': childId,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to send message: ${response.body}');
    }
  }

  Future<List<Map<String, dynamic>>> getSessions(String childId) async {
    final email = _prefs.getString('email');
    if (email == null) throw Exception('Not logged in');

    final response = await http.get(
      Uri.parse('$baseUrl/sessions/$childId'),
      headers: {
        'Authorization': email,
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data['sessions']);
    } else {
      throw Exception('Failed to get sessions: ${response.body}');
    }
  }

  Future<List<Map<String, dynamic>>> getConversations(String sessionId) async {
    final email = _prefs.getString('email');
    if (email == null) throw Exception('Not logged in');

    final response = await http.get(
      Uri.parse('$baseUrl/conversations/$sessionId'),
      headers: {
        'Authorization': email,
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(data['conversations']);
    } else {
      throw Exception('Failed to get conversations: ${response.body}');
    }
  }
} 