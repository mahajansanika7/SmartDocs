import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class DocumentService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(
      `${this.apiUrl}/uploadFile`,
      formData
    );
  }

  getDocuments() {
    return this.http.get<any>(
      `${this.apiUrl}/documents`
    );
  }

  askQuestion(query: string, document: string) {
    return this.http.post<any>(
      `${this.apiUrl}/query`,
      {
        query,
        document
      }
    );
  }

  getHistory() {
    return this.http.get<any>(
      `${this.apiUrl}/getHistory`
    );
  }

  register(username: string, password: string) {
    return this.http.post(
      `${this.apiUrl}/register`,
      {
        username,
        password
      }
    );
  }

  login(username: string, password: string) {
    return this.http.post<any>(
      `${this.apiUrl}/login`,
      {
        username,
        password
      }
    );
  }
}
