import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DocumentService } from '../../services/document';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss']
})
export class DashboardComponent implements OnInit {

  selectedFile: File | null = null;

  documents: string[] = [];

  selectedDocument = '';

  query = '';

  answer = '';

  sources: any[] = [];

  history: any[] = [];

  uploadMessage = '';

  loading = false;

  constructor(
    private documentService: DocumentService,
    private router: Router
  ) { }

  ngOnInit() {
    console.log('Dashboard initialized');
    this.loadDocuments();
    this.loadHistory();
  }

  onFileSelected(event: any) {

    this.selectedFile = event.target.files[0];
  }

  uploadFile() {

    if (!this.selectedFile) {
      return;
    }

    this.uploadMessage = 'Uploading...';

    this.documentService
      .uploadFile(this.selectedFile)
      .subscribe({

        next: (response: any) => {

          this.uploadMessage = response.message;

          this.loadDocuments();

          this.selectedDocument =
            this.selectedFile!.name;
        },

        error: (error) => {

          this.uploadMessage =
            error.error?.detail ||
            'Upload failed';
        }

      });
  }

  askQuestion() {

    if (!this.query || !this.selectedDocument) {
      return;
    }

    this.loading = true;
    this.answer = '';
    this.sources = [];

    this.documentService
      .askQuestion(
        this.query,
        this.selectedDocument
      )
      .subscribe({

        next: (response) => {

          this.answer = response.answer;

          this.sources =
            response.sources || [];

          this.loading = false;

          this.loadHistory();
        },

        error: (error) => {

          this.answer =
            error.error?.detail ||
            'Something went wrong';

          this.loading = false;
        }

      });
  }

  loadHistory() {

    this.documentService
      .getHistory()
      .subscribe({

        next: (response) => {

          this.history =
            response.history || [];

        }

      });
  }

  logout() {

    localStorage.removeItem('Token');

    this.router.navigate(['/login']);
  }

  async loadDocuments() {

    try {
      const response = await firstValueFrom(
        this.documentService.getDocuments()
      );

      console.log('Documents response:', response);

      this.documents = response.documents.map(
        (doc: any) => doc.filename
      );

      console.log('Documents array:', this.documents);

    } catch (error) {
      console.error('Failed to load documents', error);

    } 
  }
}