import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { DocumentService } from '../../services/document';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class LoginComponent {

  username = '';
  password = '';
  error = '';

  constructor(
    private documentService: DocumentService,
    private router: Router
  ) {}

  login() {

    this.error = '';

    this.documentService
      .login(this.username, this.password)
      .subscribe({
        next: (response) => {

          // this.authService.saveToken(response.token);
          console.log("sanika``````", response)
          if (!response?.token) {
            this.error = 'Invalid username or password';
            return;
          }
          localStorage.setItem("Token", response.token);

          this.router.navigate(['/dashboard']);
        },

        error: (error) => {

          this.error =
            error.error?.detail ||
            error.error?.message ||
            'Login failed';
        }
      });
  }
}