import { Component, EventEmitter, Input, Output } from "@angular/core";
import { RouterLink } from "@angular/router";
import { MatButtonModule } from "@angular/material/button";
import { Assignment, AssignmentCreateRequest, AssignmentItem, OnlineCatalog } from "../core/practice-api";
import { AssignmentForm } from "./assignment-form";

@Component({
  selector: "app-assignment-notebook",
  imports: [
    AssignmentForm,
    MatButtonModule,
    RouterLink,
  ],
  templateUrl: "./assignment-notebook.html",
  styleUrl: "./assignment-notebook.scss",
})
export class AssignmentNotebook {
  @Input() assignments: Assignment[] = [];
  @Input() catalog: OnlineCatalog | null = null;
  @Input() saving = false;
  @Output() readonly createAssignment = new EventEmitter<AssignmentCreateRequest>();
  @Output() readonly startAssignmentItem = new EventEmitter<{ assignment: Assignment; item: AssignmentItem }>();
  @Output() readonly archiveAssignment = new EventEmitter<Assignment>();

  protected get statusCounts(): { label: string; value: number }[] {
    const statuses = ["assigned", "in_progress", "completed", "archived"];
    return statuses.map((status) => ({
      label: this.statusLabel(status),
      value: this.assignments.filter((assignment) => assignment.status === status).length,
    }));
  }

  protected firstItem(assignment: Assignment): AssignmentItem | null {
    return assignment.items[0] ?? null;
  }

  protected itemSummary(assignment: Assignment): string {
    const item = this.firstItem(assignment);
    if (item === null) {
      return "No items";
    }
    return this.pluginTitle(item.plugin) + " - " + item.question_count + " questions";
  }

  protected pluginTitle(pluginId: string): string {
    return this.catalog?.plugins.find((plugin) => plugin.plugin === pluginId)?.title ?? pluginId;
  }

  protected statusLabel(status: string): string {
    return status.replace("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  protected formatDate(value: string | null | undefined): string {
    if (!value) {
      return "No date";
    }
    return new Intl.DateTimeFormat("en-CA", { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
  }

  protected canStart(assignment: Assignment): boolean {
    const item = this.firstItem(assignment);
    return item !== null && item.status !== "completed" && assignment.status !== "archived";
  }

  protected start(assignment: Assignment): void {
    const item = this.firstItem(assignment);
    if (item !== null) {
      this.startAssignmentItem.emit({ assignment, item });
    }
  }

  protected canArchive(assignment: Assignment): boolean {
    return assignment.status !== "archived" && assignment.status !== "completed";
  }
}
